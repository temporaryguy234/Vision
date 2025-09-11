from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Import our models and processors
from models import *
from lottie_processor import lottie_processor

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

# API Router
api_router = APIRouter(prefix="/api")

# Database dependency
def get_database():
    # Prefer Mongo if available, otherwise file DB
    return app.mongodb if getattr(app, 'mongodb', None) else app.file_db

# Template Upload and Processing
@api_router.post("/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    source: str = Form("upload"),
    db=Depends(get_database)
):
    """Upload and process a Lottie template file"""
    try:
        # Validate file type
        if not (file.filename.endswith('.json') or file.filename.endswith('.lottie')):
            raise HTTPException(status_code=400, detail="Only .json and .lottie files are supported")
        
        # Generate unique filename
        file_hash = hashlib.md5(file.filename.encode()).hexdigest()[:8]
        safe_name = "".join(c for c in file.filename if c.isalnum() or c in '.-_')
        unique_filename = f"{file_hash}_{safe_name}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
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
            "creator_id": "system",
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
            "creator_id": "system",
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
async def get_template(template_id: str, db=Depends(get_database)):
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
async def get_template_animation_data(template_id: str, db=Depends(get_database)):
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

# Template Revisions
@api_router.post("/templates/{template_id}/revisions")
async def save_revision(
    template_id: str,
    revision_data: TemplateRevisionCreate,
    db=Depends(get_database)
):
    """Save a template edit revision"""
    try:
        # Verify template exists
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
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
    user_id: str,
    db=Depends(get_database)
):
    """Get template revisions for a user"""
    try:
        cursor = db.template_revisions.find({
            "template_id": template_id,
            "user_id": user_id
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
        
        # Process with AI (placeholder - would integrate with LLM)
        patches = await process_ai_prompt(prompt, manifest, current_state)
        
        return {"patches": patches}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_ai_prompt(prompt: str, manifest: Dict, state: Dict) -> List[Dict]:
    """Process AI prompt and return JSON patches (placeholder implementation)"""
    patches = []
    
    # Simple pattern matching for demo
    prompt_lower = prompt.lower()
    
    # Speed changes
    if "faster" in prompt_lower or "speed" in prompt_lower:
        if "30%" in prompt_lower or "faster" in prompt_lower:
            patches.append({
                "op": "replace",
                "path": "/speed",
                "value": 1.3
            })
    
    # Text changes
    if "title" in prompt_lower and "hello world" in prompt_lower:
        text_elements = manifest.get("text", [])
        if text_elements:
            patches.append({
                "op": "replace", 
                "path": f"/text/{text_elements[0]['id']}",
                "value": "Hello World"
            })
    
    # Color changes
    if "primary color" in prompt_lower and "#" in prompt:
        color_match = None
        import re
        hex_match = re.search(r'#[0-9a-fA-F]{6}', prompt)
        if hex_match:
            color_elements = manifest.get("colors", [])
            if color_elements:
                patches.append({
                    "op": "replace",
                    "path": f"/colors/{color_elements[0]['id']}",
                    "value": hex_match.group()
                })
    
# Include router
app.include_router(api_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)