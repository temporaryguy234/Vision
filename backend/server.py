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
from datetime import datetime

# Import our models and processors
from models import *
from lottie_processor import lottie_processor
from preview_generator import generate_preview
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = "motionedit"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = AsyncIOMotorClient(MONGO_URL)
    app.mongodb = app.mongodb_client[DB_NAME]
    logger.info("Connected to MongoDB")
    yield
    # Shutdown
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

# Create uploads directory
UPLOADS_DIR = Path("/app/uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# API Router
api_router = APIRouter(prefix="/api")

# Database dependency
def get_database():
    return app.mongodb

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

        # Generate preview image
        preview_path = UPLOADS_DIR / "previews" / f"{unique_filename}.png"
        generate_preview(file_path, preview_path)
        preview_url = f"/uploads/previews/{unique_filename}.png"
        
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
        
        # Generate preview image
        preview_path = UPLOADS_DIR / "previews" / f"{unique_filename}.png"
        generate_preview(file_path, preview_path)
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
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db=Depends(get_database)
):
    """Get templates with optional filtering"""
    try:
        filter_query = {}
        if category:
            filter_query["category"] = category

        if search:
            # Case-insensitive search on title and tags
            filter_query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"tags": {"$regex": search, "$options": "i"}},
            ]

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

@api_router.patch("/templates/{template_id}")
async def update_template(template_id: str, update: TemplateUpdate, db=Depends(get_database)):
    """Update fields on a template"""
    try:
        update_data = update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        update_data["updated_at"] = datetime.utcnow()
        result = await db.templates.update_one({"id": template_id}, {"$set": update_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        template = await db.templates.find_one({"id": template_id})
        return Template(**template)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str, db=Depends(get_database)):
    """Delete a template"""
    try:
        result = await db.templates.delete_one({"id": template_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete template error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/templates/{template_id}/data")
async def get_template_animation_data(template_id: str, db=Depends(get_database)):
    """Get the original animation data for a template"""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Read the animation file
        file_path = Path("/app" + template["file_url"])
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
class PromptRequest(BaseModel):
    prompt: str

def _parse_prompt(prompt: str) -> Dict[str, str]:
    """Very small parser that maps 'key: value' pairs from a prompt."""
    updates: Dict[str, str] = {}
    for part in prompt.split(";"):
        if ":" in part:
            key, value = part.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key in {"title", "description"}:
                updates[key] = value
    return updates

@api_router.post("/templates/{template_id}/prompt")
async def process_prompt(template_id: str, request: PromptRequest, db=Depends(get_database)):
    """Apply simple prompt-based updates to a template."""
    try:
        template = await db.templates.find_one({"id": template_id})
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        updates = _parse_prompt(request.prompt)
        if updates:
            updates["updated_at"] = datetime.utcnow()
            await db.templates.update_one({"id": template_id}, {"$set": updates})
            template.update(updates)
        return {"updated_fields": list(updates.keys()), "template": Template(**template)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include router
app.include_router(api_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
