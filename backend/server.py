from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Request
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors as mongo_errors
from contextlib import asynccontextmanager
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import aiofiles
import hashlib
from datetime import datetime

# Import our models and processors
from models import *
from lottie_processor import lottie_processor
from file_storage import FileStorageManager
from auth import AuthService, get_current_user, get_current_user_optional, User, UserCreate, UserLogin, GoogleAuthRequest
from subscription import SubscriptionService, SubscriptionTier
from payments import PaymentService, PaymentIntent
from ai_service import ai_service, AIPromptRequest
from export_service import ExportService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = "motionedit"

class FileCursor:
    def __init__(self, items):
        self._items = items
        self._skip = 0
        self._limit = None
        self._sort = None

    def skip(self, n: int):
        self._skip = n
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def sort(self, key: str, direction: int):
        reverse = direction < 0
        self._sort = (key, reverse)
        return self

    async def to_list(self, length=None):
        items = list(self._items)
        if self._sort:
            key, reverse = self._sort
            items.sort(key=lambda x: x.get(key), reverse=reverse)
        if self._skip:
            items = items[self._skip :]
        if self._limit is not None:
            items = items[: self._limit]
        return items


class FileCollection:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_sync([])

    async def insert_one(self, doc: Dict[str, Any]):
        docs = await self._read()
        docs.append(doc)
        await self._write(docs)
        return {"inserted_id": doc.get("id")}

    def find(self, filter_query: Dict[str, Any]):
        # Simple filtering supporting equality only
        docs = self._read_sync()
        def match(d):
            for k, v in filter_query.items():
                if d.get(k) != v:
                    return False
            return True
        matched = [d for d in docs if match(d)] if filter_query else docs
        return FileCursor(matched)

    async def find_one(self, filter_query: Dict[str, Any]):
        cursor = self.find(filter_query)
        items = await cursor.to_list()
        return items[0] if items else None

    async def update_one(self, filter_query: Dict[str, Any], update: Dict[str, Any]):
        docs = await self._read()
        matched = 0
        for i, d in enumerate(docs):
            ok = True
            for k, v in filter_query.items():
                if d.get(k) != v:
                    ok = False
                    break
            if ok:
                set_data = update.get("$set", {})
                d.update(set_data)
                docs[i] = d
                matched = 1
                break
        if matched:
            await self._write(docs)
        return type("Res", (), {"matched_count": matched})

    async def delete_many(self, filter_query: Dict[str, Any]):
        docs = await self._read()
        if not filter_query:
            deleted = len(docs)
            docs = []
        else:
            before = len(docs)
            def match(d):
                for k, v in filter_query.items():
                    if d.get(k) != v:
                        return False
                return True
            docs = [d for d in docs if not match(d)]
            deleted = before - len(docs)
        await self._write(docs)
        return {"deleted_count": deleted}

    async def count_documents(self, filter_query: Dict[str, Any]):
        return len(await self.find(filter_query).to_list())

    async def _read(self):
        async with aiofiles.open(self.file_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content or "[]")

    def _read_sync(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.loads(f.read() or "[]")
        except FileNotFoundError:
            return []

    async def _write(self, docs: List[Dict[str, Any]]):
        async with aiofiles.open(self.file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(docs, indent=2))

    def _write_sync(self, docs: List[Dict[str, Any]]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(docs, indent=2))


class FileDB:
    def __init__(self, base_dir: Path):
        db_dir = base_dir / "db"
        self.templates = FileCollection(db_dir / "templates.json")
        self.template_revisions = FileCollection(db_dir / "template_revisions.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: try Mongo, otherwise fallback to file DB
    use_file_db = False
    app.mongodb_client = None
    app.mongodb = None
    try:
        app.mongodb_client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=1000)
        await app.mongodb_client.admin.command("ping")
        app.mongodb = app.mongodb_client[DB_NAME]
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.warning(f"MongoDB not available, using file DB. Reason: {e}")
        use_file_db = True

    # Expose unified db accessor
    app.file_db = FileDB(Path(os.environ.get('UPLOADS_DIR', str(Path(__file__).parent.parent / 'uploads')))) if use_file_db else None

    yield

    # Shutdown
    if app.mongodb_client:
        app.mongodb_client.close()

app = FastAPI(title="MotionEdit API", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory (configurable)
UPLOADS_DIR = Path(os.environ.get('UPLOADS_DIR', str(Path(__file__).parent.parent / 'uploads')))
UPLOADS_DIR.mkdir(exist_ok=True, parents=True)
(
    UPLOADS_DIR / "previews"
).mkdir(exist_ok=True, parents=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/exports", StaticFiles(directory="/app/exports"), name="exports")

# API Router
api_router = APIRouter(prefix="/api")

# Database dependency
def get_database():
    # Prefer Mongo if available, otherwise file DB
    return app.mongodb if getattr(app, 'mongodb', None) else app.file_db

file_storage_manager = FileStorageManager(base_upload_dir=str(UPLOADS_DIR))

# Initialize services
def get_auth_service(db=Depends(get_database)):
    return AuthService(db)

def get_subscription_service(db=Depends(get_database)):
    return SubscriptionService(db)

def get_payment_service(db=Depends(get_database)):
    return PaymentService(db)

def get_export_service(db=Depends(get_database)):
    return ExportService(db, file_storage_manager)

# Authentication Routes
@api_router.post("/auth/register")
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    user = await auth_service.register_user(user_data)
    token = auth_service.create_access_token(user.id, user.email)
    
    return {
        "user": user,
        "access_token": token,
        "token_type": "bearer"
    }

@api_router.post("/auth/login")
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user"""
    user, token = await auth_service.authenticate_user(login_data)
    
    return {
        "user": user,
        "access_token": token,
        "token_type": "bearer"
    }

@api_router.post("/auth/google")
async def google_auth(
    auth_request: GoogleAuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate with Google"""
    user, token = await auth_service.google_auth(auth_request)
    
    return {
        "user": user,
        "access_token": token,
        "token_type": "bearer"
    }

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Subscription Routes
@api_router.get("/subscriptions/plans")
async def get_subscription_plans(
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get all subscription plans"""
    return subscription_service.get_all_plans()

@api_router.get("/subscriptions/current")
async def get_current_subscription(
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get user's current subscription"""
    subscription = await subscription_service.get_user_subscription(current_user.id)
    return {
        "subscription": subscription,
        "plan": subscription_service.get_plan(SubscriptionTier(current_user.subscription_tier))
    }

@api_router.post("/subscriptions/upgrade")
async def upgrade_subscription(
    tier: SubscriptionTier,
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Upgrade user subscription"""
    subscription = await subscription_service.create_subscription(
        current_user.id, 
        tier
    )
    return subscription

# Payment Routes
@api_router.post("/payments/create-intent")
async def create_payment_intent(
    payment_data: PaymentIntent,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Create payment intent"""
    if payment_data.payment_method == "stripe":
        result = await payment_service.create_stripe_payment_intent(
            current_user.id,
            payment_data.amount,
            payment_data.subscription_tier
        )
    elif payment_data.payment_method == "paypal":
        result = await payment_service.create_paypal_payment(
            current_user.id,
            payment_data.amount,
            payment_data.subscription_tier
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid payment method")
    
    return result

@api_router.post("/payments/stripe/webhook")
async def stripe_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    success = await payment_service.handle_stripe_webhook(payload, sig_header)
    
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Webhook processing failed")

@api_router.post("/payments/paypal/confirm")
async def confirm_paypal_payment(
    payment_id: str,
    payer_id: str,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Confirm PayPal payment"""
    success = await payment_service.confirm_paypal_payment(payment_id, payer_id)
    
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Payment confirmation failed")

# Template Upload and Processing
@api_router.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    source: str = Form("upload"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    """Upload and process a Lottie template file"""
    try:
        # Validate file type
        if not (file.filename.endswith('.json') or file.filename.endswith('.lottie')):
            raise HTTPException(status_code=400, detail="Only .json and .lottie files are supported")
        
        # Read file content and generate a unique filename based on its hash
        content = await file.read()
        file_hash = hashlib.md5(content).hexdigest()[:8]
        safe_name = "".join(c for c in file.filename if c.isalnum() or c in '.-_')
        unique_filename = f"{file_hash}_{safe_name}"
        file_path = UPLOADS_DIR / unique_filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Process file
        animation_data, manifest = await lottie_processor.process_file(file_path)
        
        # Generate preview (placeholder for now)
        preview_url = f"/uploads/previews/{unique_filename}.png"
        preview_video_url = ""
        
        # Generate proper slug
        base_name = file.filename.replace('.json', '').replace('.lottie', '')
        safe_slug = base_name.lower().replace(' ', '-').replace('_', '-')
        safe_slug = ''.join(c for c in safe_slug if c.isalnum() or c == '-')
        
        # Create template record
        template_data = {
            "title": base_name,
            "description": f"Imported from {source}",
            "tags": [],
            "source": source,
            "license": "",
            "author": "",
            "creator_id": current_user.id,
            "file_url": f"/uploads/{unique_filename}",
            "preview_url": preview_url,
            "manifest": manifest,
            "category": TemplateCategory.MISCELLANEOUS,
            # Add required fields for Template model compatibility
            "slug": safe_slug,
            "preview_image_url": preview_url,
            "preview_video_url": preview_video_url,
            "editable_parameters_schema": {
                "canvas": {"width": 400, "height": 400, "background_color": "#FFFFFF", "global_playback_speed": 1.0},
                "elements": []
            },
            "is_public": True
        }
        
        template = Template(**template_data)
        result = await db.templates.insert_one(template.model_dump())
        
        return {
            "id": template.id,
            "name": template.title,
            "preview_url": template.preview_url,
            "manifest": template.manifest,
            "file_url": template.file_url
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/templates/import-url")
async def import_from_url(
    url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    """Import a Lottie template from URL"""
    try:
        # Process URL
        animation_data, manifest = await lottie_processor.process_url(url)
        
        # Generate filename from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        filename = Path(parsed_url.path).name or "imported_animation.json"
        
        # Save locally
        file_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        unique_filename = f"{file_hash}_{filename}"
        file_path = UPLOADS_DIR / unique_filename
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(animation_data, indent=2))
        
        # Generate preview
        preview_url = f"/uploads/previews/{unique_filename}.png"
        
        # Generate proper slug
        base_name = filename.replace('.json', '').replace('.lottie', '')
        safe_slug = base_name.lower().replace(' ', '-').replace('_', '-')
        safe_slug = ''.join(c for c in safe_slug if c.isalnum() or c == '-')
        
        # Create template record
        template_data = {
            "title": filename.replace('.json', '').replace('.lottie', ''),
            "description": f"Imported from URL: {url}",
            "tags": [],
            "source": "url",
            "license": "",
            "author": "",
            "creator_id": current_user.id,
            "file_url": f"/uploads/{unique_filename}",
            "preview_url": preview_url,
            "manifest": manifest,
            "category": TemplateCategory.MISCELLANEOUS,
            # Add required fields for Template model compatibility
            "slug": safe_slug,
            "preview_image_url": preview_url,
            "editable_parameters_schema": {
                "canvas": {"width": 400, "height": 400, "background_color": "#FFFFFF", "global_playback_speed": 1.0},
                "elements": []
            },
            "is_public": True
        }
        
        template = Template(**template_data)
        result = await db.templates.insert_one(template.model_dump())
        
        return {
            "id": template.id,
            "name": template.title,
            "preview_url": template.preview_url,
            "manifest": template.manifest,
            "file_url": template.file_url
        }
        
    except Exception as e:
        logger.error(f"URL import error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template CRUD Operations
@api_router.get("/templates")
async def get_templates(
    category: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db=Depends(get_database)
):
    """Get templates with optional filtering"""
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category
        
        cursor = db.templates.find(filter_query).skip(skip).limit(limit)
        templates = await cursor.to_list(length=None)
        
        return [Template(**template) for template in templates]
        
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/{template_id}")
async def get_template(
    template_id: str, 
    current_user: Optional[User] = Depends(get_current_user_optional),
    db=Depends(get_database)
):
    """Get a specific template by ID"""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return Template(**template)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/{template_id}/data")
async def get_template_animation_data(
    template_id: str, 
    current_user: Optional[User] = Depends(get_current_user_optional),
    db=Depends(get_database)
):
    """Get the original animation data for a template"""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Read the animation file
        file_url: str = template.get("file_url", "")
        if not file_url.startswith("/uploads/"):
            raise HTTPException(status_code=404, detail="Invalid animation file path")
        relative = file_url[len("/uploads/"):]
        file_path = UPLOADS_DIR / relative
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Animation file not found")
        
        animation_data, _ = await lottie_processor.process_file(file_path)
        return animation_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get animation data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Previews upload (client-side generated)
@api_router.post("/templates/{template_id}/previews")
async def upload_template_previews(
    template_id: str,
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db=Depends(get_database)
):
    try:
        # Verify template exists
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        preview_image_url = template.get("preview_image_url", "")
        preview_video_url = template.get("preview_video_url", "")

        # Save image
        if image is not None:
            # Force into previews subdir
            previews_dir = UPLOADS_DIR / "previews"
            previews_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{template_id}_thumb.png"
            file_path = previews_dir / filename
            async with aiofiles.open(file_path, 'wb') as f:
                content = await image.read()
                await f.write(content)
            preview_image_url = f"/uploads/previews/{filename}"

        # Save video
        if video is not None:
            previews_dir = UPLOADS_DIR / "previews"
            previews_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{template_id}_preview.webm"
            file_path = previews_dir / filename
            async with aiofiles.open(file_path, 'wb') as f:
                content = await video.read()
                await f.write(content)
            preview_video_url = f"/uploads/previews/{filename}"

        # Update template
        update_data = {
            "preview_image_url": preview_image_url,
            "preview_video_url": preview_video_url,
            "updated_at": datetime.utcnow()
        }
        await db.templates.update_one({"id": template_id}, {"$set": update_data})

        return {
            "preview_image_url": preview_image_url,
            "preview_video_url": preview_video_url
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload previews error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template Revisions
@api_router.post("/templates/{template_id}/revisions")
async def save_revision(
    template_id: str,
    revision_data: TemplateRevisionCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    """Save a template edit revision"""
    try:
        # Verify template exists
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Set user_id from current user
        revision_data.user_id = current_user.id
        revision = TemplateRevision(**revision_data.model_dump())
        await db.template_revisions.insert_one(revision.model_dump())
        
        return {"id": revision.id, "template_id": template_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save revision error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/{template_id}/revisions")
async def get_revisions(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get template revisions for a user"""
    try:
        cursor = db.template_revisions.find({
            "template_id": template_id,
            "user_id": current_user.id
        }).sort("created_at", -1).limit(10)
        
        revisions = await cursor.to_list(length=None)
        return [TemplateRevision(**revision) for revision in revisions]
        
    except Exception as e:
        logger.error(f"Get revisions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Prompt Processing
@api_router.post("/templates/{template_id}/prompt")
async def process_prompt(
    template_id: str,
    prompt_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db=Depends(get_database)
):
    """Process natural language prompt and return JSON patches"""
    try:
        # Get template
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        prompt = prompt_data.get("prompt", "")
        current_state = prompt_data.get("state", {})
        manifest = template.get("manifest", {})
        
        # Process with AI
        ai_response = await ai_service.process_natural_language_prompt(
            prompt, manifest, current_state
        )
        
        return {
            "patches": ai_response.patches,
            "explanation": ai_response.explanation,
            "confidence": ai_response.confidence
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export Routes
@api_router.post("/exports/create")
async def create_export(
    template_id: str,
    current_state: Dict[str, Any],
    export_format: str = "MP4",
    resolution: str = "1080p",
    current_user: User = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    export_service: ExportService = Depends(get_export_service)
):
    """Create export job"""
    # Check subscription permissions
    if not await subscription_service.check_export_permissions(current_user, resolution):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Your subscription doesn't support {resolution} exports"
        )
    
    # Use credit
    await subscription_service.use_credit(current_user.id)
    
    # Check if watermark should be added
    add_watermark = subscription_service.should_add_watermark(current_user)
    
    # Create export
    result = await export_service.export_animation(
        current_user.id,
        template_id,
        current_state,
        export_format,
        resolution,
        add_watermark
    )
    
    return result

@api_router.get("/exports")
async def get_user_exports(
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """Get user's exports"""
    exports = await export_service.get_user_exports(current_user.id)
    return exports

@api_router.delete("/exports/{export_id}")
async def delete_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service)
):
    """Delete an export"""
    success = await export_service.delete_export(export_id, current_user.id)
    if success:
        return {"message": "Export deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Export not found")

# Include router
app.include_router(api_router)

# Bulk Import Routes (Enhanced)
@api_router.post("/bulk-import/upload")
async def bulk_import_upload(
    files: List[UploadFile] = File(...),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Enhanced bulk upload with authentication"""
    results = []
    
    for file in files:
        try:
            file_url, asset_type, metadata = await file_storage_manager.save_uploaded_file(file)
            
            # Check for duplicates using file hash
            file_hash = metadata.get('file_hash')
            if file_hash:
                existing_template = await db.templates.find_one({"file_hash": file_hash})
                if existing_template:
                    results.append({
                        "filename": file.filename,
                        "status": "duplicate",
                        "existing_template_id": existing_template['id'],
                        "message": "File already exists in library"
                    })
                    continue
            
            # Generate thumbnail
            thumbnail_url = await file_storage_manager.generate_thumbnail(file_url, asset_type)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "file_url": file_url,
                "asset_type": asset_type.value,
                "metadata": metadata,
                "thumbnail_url": thumbnail_url,
                "file_hash": file_hash
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
    
    return {"results": results}
# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@api_router.post("/bulk-import/create-templates")
async def bulk_import_create_templates(
    import_data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create templates from bulk import data"""
    items = import_data.get('items', [])
    templates_created = []
    errors = []
    
    for item in items:
        try:
            # Generate slug
            title = item.get('title', item.get('filename', 'Untitled'))
            slug = title.lower().replace(' ', '-').replace('_', '-')
            slug = ''.join(c for c in slug if c.isalnum() or c == '-')
            
            # Create template
            template_data = {
                "title": title,
                "slug": slug,
                "category": item.get('category', 'Miscellaneous'),
                "tags": item.get('tags', []),
                "preview_image_url": item.get('thumbnail_url', ''),
                "preview_video_url": "",
                "file_url": item.get('file_url', ''),
                "manifest": item.get('manifest', {}),
                "creator_id": current_user.id if current_user else "anonymous",
                "is_public": item.get('is_public', True),
                "editable_parameters_schema": {
                    "canvas": {
                        "width": item.get('metadata', {}).get('width', 800),
                        "height": item.get('metadata', {}).get('height', 600),
                        "background_color": "#FFFFFF",
                        "global_playback_speed": 1.0
                    },
                    "elements": []
                }
            }
            
            template = Template(**template_data)
            await db.templates.insert_one(template.model_dump())
            
            templates_created.append({
                "template_id": template.id,
                "title": template.title,
                "filename": item.get('filename')
            })
            
        except Exception as e:
            errors.append({
                "filename": item.get('filename', 'unknown'),
                "error": str(e)
            })
    
    return {
        "templates_created": templates_created,
        "errors": errors,
        "summary": {
            "successful": len(templates_created),
            "failed": len(errors),
            "total": len(items)
        }
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)