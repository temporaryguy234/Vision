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
        
        # Generate preview (placeholder for now)
        preview_url = f"/uploads/previews/{unique_filename}.png"
        
        # Create template record
        template_data = {
            "name": file.filename.replace('.json', '').replace('.lottie', ''),
            "description": f"Imported from {source}",
            "tags": [],
            "source": source,
            "license": "",
            "author": "",
            "file_url": f"/uploads/{unique_filename}",
            "preview_url": preview_url,
            "manifest": manifest,
            "category": TemplateCategory.MISCELLANEOUS
        }
        
        template = Template(**template_data)
        result = await db.templates.insert_one(template.model_dump())
        
        return {
            "id": template.id,
            "name": template.name,
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
        
        # Create template record
        template_data = {
            "name": filename.replace('.json', '').replace('.lottie', ''),
            "description": f"Imported from URL: {url}",
            "tags": [],
            "source": "url",
            "license": "",
            "author": "",
            "file_url": f"/uploads/{unique_filename}",
            "preview_url": preview_url,
            "manifest": manifest,
            "category": TemplateCategory.MISCELLANEOUS
        }
        
        template = Template(**template_data)
        result = await db.templates.insert_one(template.model_dump())
        
        return {
            "id": template.id,
            "name": template.name,
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

# API Routes

# Root endpoint
@api_router.get("/")
async def root():
    return {
        "message": "MotionEdit API v2.0.0",
        "description": "Comprehensive Motion Graphics Template Platform",
        "version": "2.0.0"
    }

# Template Routes
@api_router.get("/templates", response_model=List[Template])
async def get_templates(
    category: Optional[TemplateCategory] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
    creator_id: Optional[str] = None,
    is_public: Optional[bool] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0),
    sort_by: str = Query("created_at", pattern="^(created_at|title|download_count|rating)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """Get templates with advanced filtering and sorting"""
    query = {}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"tags": {"$in": [search]}},
        ]
    
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        query["tags"] = {"$in": tag_list}
    
    if creator_id:
        query["creator_id"] = creator_id
    
    if is_public is not None:
        query["is_public"] = is_public
    
    # Sort configuration
    sort_direction = 1 if sort_order == "asc" else -1
    sort_config = [(sort_by, sort_direction)]
    
    templates = await db.templates.find(query).sort(sort_config).skip(skip).limit(limit).to_list(limit)
    return [Template(**template) for template in templates]

@api_router.post("/templates", response_model=Template)
async def create_template(template: TemplateCreate):
    """Create a new template with validation"""
    # Validate editable parameters
    validation_errors = validator.validate_editable_parameters(template.editable_parameters_schema)
    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid editable parameters",
                "errors": validation_errors
            }
        )
    
    # Create slug from title
    slug = create_slug(template.title)
    unique_slug = await ensure_unique_slug(slug)
    
    template_dict = template.model_dump()
    template_dict["slug"] = unique_slug
    
    template_obj = Template(**template_dict)
    
    await db.templates.insert_one(template_obj.model_dump())
    return template_obj

@api_router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get a specific template by ID"""
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return Template(**template)

@api_router.get("/templates/slug/{slug}", response_model=Template)
async def get_template_by_slug(slug: str):
    """Get a specific template by slug"""
    template = await db.templates.find_one({"slug": slug})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return Template(**template)

@api_router.put("/templates/{template_id}", response_model=Template)
async def update_template(template_id: str, template_update: TemplateUpdate):
    """Update a template"""
    # Check if template exists
    existing_template = await db.templates.find_one({"id": template_id})
    if not existing_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = {k: v for k, v in template_update.model_dump().items() if v is not None}
    
    # Validate editable parameters if provided
    if "editable_parameters_schema" in update_data:
        validation_errors = validator.validate_editable_parameters(update_data["editable_parameters_schema"])
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid editable parameters",
                    "errors": validation_errors
                }
            )
    
    # Update slug if title changed
    if "title" in update_data:
        new_slug = create_slug(update_data["title"])
        unique_slug = await ensure_unique_slug(new_slug, template_id)
        update_data["slug"] = unique_slug
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    updated_template = await db.templates.find_one({"id": template_id})
    return Template(**updated_template)

@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template and its assets"""
    # Check if template exists
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Delete associated assets
    assets = await db.template_assets.find({"template_id": template_id}).to_list(None)
    for asset in assets:
        await file_storage.delete_file(asset["file_url"])
    
    # Delete assets from database
    await db.template_assets.delete_many({"template_id": template_id})
    
    # Delete template
    await db.templates.delete_one({"id": template_id})
    
    return {"message": "Template deleted successfully"}

# Template Assets Routes
@api_router.get("/templates/{template_id}/assets", response_model=List[TemplateAsset])
async def get_template_assets(template_id: str):
    """Get all assets for a template"""
    assets = await db.template_assets.find({"template_id": template_id}).to_list(None)
    return [TemplateAsset(**asset) for asset in assets]

@api_router.post("/templates/{template_id}/assets", response_model=TemplateAsset)
async def create_template_asset(template_id: str, asset: TemplateAssetCreate):
    """Create a new template asset"""
    # Verify template exists
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    asset_dict = asset.model_dump()
    asset_obj = TemplateAsset(**asset_dict)
    
    await db.template_assets.insert_one(asset_obj.model_dump())
    return asset_obj

@api_router.post("/templates/{template_id}/upload-asset", response_model=TemplateAsset)
async def upload_template_asset(
    template_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """Upload a file asset for a template"""
    # Verify template exists
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Save file and get metadata
    file_url, asset_type, metadata = await file_storage.save_uploaded_file(file, template_id)
    
    # Create asset record
    asset_data = {
        "template_id": template_id,
        "asset_type": asset_type,
        "file_url": file_url,
        "width": metadata.get('width'),
        "height": metadata.get('height'),
        "duration": metadata.get('duration'),
        "frame_rate": metadata.get('frame_rate'),
        "file_size": metadata.get('file_size', 0)
    }
    
    asset_obj = TemplateAsset(**asset_data)
    await db.template_assets.insert_one(asset_obj.model_dump())
    
    return asset_obj

@api_router.delete("/templates/{template_id}/assets/{asset_id}")
async def delete_template_asset(template_id: str, asset_id: str):
    """Delete a template asset"""
    asset = await db.template_assets.find_one({"id": asset_id, "template_id": template_id})
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Delete file
    await file_storage.delete_file(asset["file_url"])
    
    # Delete from database
    await db.template_assets.delete_one({"id": asset_id})
    
    return {"message": "Asset deleted successfully"}

# Project Routes
@api_router.get("/projects", response_model=List[Project])
async def get_projects(
    user_id: str,
    status: Optional[ProjectStatus] = None,
    template_id: Optional[str] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user projects"""
    query = {"user_id": user_id}
    
    if status:
        query["status"] = status
    
    if template_id:
        query["template_id"] = template_id
    
    projects = await db.projects.find(query).sort([("updated_at", -1)]).skip(skip).limit(limit).to_list(limit)
    return [Project(**project) for project in projects]

@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    """Create a new project from a template"""
    # Verify template exists
    template = await db.templates.find_one({"id": project.template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Initialize editor state with template's editable parameters
    initial_state = {
        "canvas": template["editable_parameters_schema"]["canvas"],
        "elements": {}
    }
    
    # Initialize each element with its default parameters
    for element in template["editable_parameters_schema"]["elements"]:
        initial_state["elements"][element["id"]] = element["parameters"]
    
    project_dict = project.model_dump()
    project_dict["current_editor_state"] = initial_state
    
    project_obj = Project(**project_dict)
    
    await db.projects.insert_one(project_obj.model_dump())
    return project_obj

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_update: ProjectUpdate):
    """Update project"""
    update_data = {k: v for k, v in project_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.projects.update_one(
        {"id": project_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_project = await db.projects.find_one({"id": project_id})
    return Project(**updated_project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

# Brand Kit Routes
@api_router.get("/brand-kits", response_model=List[BrandKit])
async def get_brand_kits(
    user_id: str,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user brand kits"""
    brand_kits = await db.brand_kits.find({"user_id": user_id}).skip(skip).limit(limit).to_list(limit)
    return [BrandKit(**kit) for kit in brand_kits]

@api_router.post("/brand-kits", response_model=BrandKit)
async def create_brand_kit(brand_kit: BrandKitCreate):
    """Create a new brand kit"""
    brand_kit_obj = BrandKit(**brand_kit.model_dump())
    await db.brand_kits.insert_one(brand_kit_obj.model_dump())
    return brand_kit_obj

@api_router.put("/brand-kits/{kit_id}", response_model=BrandKit)
async def update_brand_kit(kit_id: str, brand_kit_update: BrandKitUpdate):
    """Update a brand kit"""
    update_data = {k: v for k, v in brand_kit_update.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.brand_kits.update_one(
        {"id": kit_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    
    updated_kit = await db.brand_kits.find_one({"id": kit_id})
    return BrandKit(**updated_kit)

@api_router.delete("/brand-kits/{kit_id}")
async def delete_brand_kit(kit_id: str):
    """Delete a brand kit"""
    result = await db.brand_kits.delete_one({"id": kit_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return {"message": "Brand kit deleted successfully"}

# Export Routes
@api_router.get("/exports", response_model=List[Export])
async def get_exports(
    user_id: str,
    project_id: Optional[str] = None,
    status: Optional[ExportStatus] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user exports"""
    query = {"user_id": user_id}
    
    if project_id:
        query["project_id"] = project_id
    
    if status:
        query["status"] = status
    
    exports = await db.exports.find(query).sort([("created_at", -1)]).skip(skip).limit(limit).to_list(limit)
    return [Export(**export) for export in exports]

@api_router.post("/exports", response_model=Export)
async def create_export(export_data: ExportCreate):
    """Create a new export job"""
    # Verify project exists
    project = await db.projects.find_one({"id": export_data.project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    export_obj = Export(**export_data.model_dump())
    await db.exports.insert_one(export_obj.model_dump())
    
    # Here you would typically queue the export job for background processing
    # For now, we'll just return the export record
    
    return export_obj

@api_router.get("/exports/{export_id}", response_model=Export)
async def get_export(export_id: str):
    """Get a specific export"""
    export = await db.exports.find_one({"id": export_id})
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    return Export(**export)

@api_router.put("/exports/{export_id}/status")
async def update_export_status(
    export_id: str,
    status: ExportStatus,
    progress: Optional[int] = Query(None, ge=0, le=100),
    download_url: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Update export status (typically called by background processing service)"""
    update_data = {
        "status": status,
        "updated_at": datetime.utcnow()
    }
    
    if progress is not None:
        update_data["progress"] = progress
    
    if download_url:
        update_data["download_url"] = download_url
    
    if error_message:
        update_data["error_message"] = error_message
    
    if status == ExportStatus.DONE:
        update_data["completed_at"] = datetime.utcnow()
    
    result = await db.exports.update_one(
        {"id": export_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Export not found")
    
    return {"message": "Export status updated"}

# Statistics Routes
@api_router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    template_count = await db.templates.count_documents({"is_public": True})
    project_count = await db.projects.count_documents({})
    export_count = await db.exports.count_documents({})
    
    return {
        "templates": f"{template_count}+",
        "projects": f"{project_count}+",
        "exports": f"{export_count}+",
        "active_creators": "10K+",
        "time_saved": "95%",
        "avg_edit_time": "2 Min"
    }

# Bulk Import Routes
@api_router.post("/bulk-import/upload")
async def bulk_import_upload(files: List[UploadFile] = File(...)):
    """Upload multiple files for bulk template import"""
    import hashlib
    
    results = []
    
    for file in files:
        try:
            # Calculate file hash for duplicate detection
            content = await file.read()
            file_hash = hashlib.md5(content).hexdigest()
            
            # Reset file pointer
            await file.seek(0)
            
            # Check for duplicates based on hash
            existing_asset = await db.template_assets.find_one({"file_hash": file_hash})
            if existing_asset:
                results.append({
                    "filename": file.filename,
                    "status": "duplicate",  
                    "message": "File already exists",
                    "existing_template_id": existing_asset.get("template_id")
                })
                continue
            
            try:
                # Process file
                file_url, asset_type, metadata = await file_storage.save_uploaded_file(file)
                
                # Generate thumbnail if possible
                thumbnail_url = await file_storage.generate_thumbnail(file_url, asset_type)
                
                result = {
                    "filename": file.filename,
                    "status": "success",
                    "file_url": file_url,
                    "asset_type": asset_type.value,
                    "metadata": metadata,
                    "thumbnail_url": thumbnail_url,
                    "file_hash": file_hash
                }
                
                results.append(result)
                
            except HTTPException as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": str(e.detail)
                })
                
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error", 
                "message": f"Unexpected error: {str(e)}"
            })
    
    return {"results": results}

@api_router.post("/bulk-import/create-templates")
async def bulk_import_create_templates(
    import_data: Dict[str, Any]
):
    """Create templates from bulk import data"""
    
    templates_created = []
    errors = []
    
    for item in import_data.get("items", []):
        try:
            # Extract template data
            template_data = {
                "title": item.get("title", f"Imported Template {len(templates_created) + 1}"),
                "category": TemplateCategory(item.get("category", "MISCELLANEOUS")),
                "tags": item.get("tags", []),
                "preview_image_url": item.get("thumbnail_url") or item.get("preview_image_url", "https://placeholder.com/300x200"),
                "creator_id": item.get("creator_id", "bulk_import"),
                "is_public": item.get("is_public", True)
            }
            
            # Create basic editable parameters schema
            if item.get("asset_type") == "Lottie JSON":
                # Create Lottie-based template
                editable_parameters = {
                    "canvas": {
                        "width": item.get("metadata", {}).get("width", 800),
                        "height": item.get("metadata", {}).get("height", 600),
                        "background_color": "transparent",
                        "global_playback_speed": 1.0
                    },
                    "elements": [
                        {
                            "id": "lottie_main",
                            "type": "lottie",
                            "name": "Main Animation",
                            "parameters": {
                                "source_url": item.get("file_url"),
                                "loop": True,
                                "autoplay": True,
                                "speed": 1.0,
                                "opacity": 1.0,
                                "x": 50.0,
                                "y": 50.0,
                                "scale": 1.0,
                                "rotation": 0.0
                            }
                        }
                    ]
                }
            else:
                # Create video/image-based template
                editable_parameters = {
                    "canvas": {
                        "width": item.get("metadata", {}).get("width", 800),
                        "height": item.get("metadata", {}).get("height", 600),
                        "background_color": "#FFFFFF",
                        "global_playback_speed": 1.0
                    },
                    "elements": [
                        {
                            "id": "media_main",
                            "type": "image",
                            "name": "Main Media",
                            "parameters": {
                                "source_url": item.get("file_url"),
                                "fit": "cover",
                                "opacity": 1.0,
                                "x": 50.0,
                                "y": 50.0,
                                "scale": 1.0,
                                "rotation": 0.0
                            }
                        }
                    ]
                }
            
            template_data["editable_parameters_schema"] = EditableParametersSchema(**editable_parameters)
            
            # Create template
            template_create = TemplateCreate(**template_data)
            
            # Validate parameters
            validation_errors = validator.validate_editable_parameters(template_create.editable_parameters_schema)
            if validation_errors:
                errors.append({
                    "filename": item.get("filename"),
                    "errors": validation_errors
                })
                continue
            
            # Create slug and ensure uniqueness
            slug = create_slug(template_create.title)
            unique_slug = await ensure_unique_slug(slug)
            
            template_dict = template_create.model_dump()
            template_dict["slug"] = unique_slug
            
            template_obj = Template(**template_dict)
            await db.templates.insert_one(template_obj.model_dump())
            
            # Create template asset record
            asset_data = {
                "template_id": template_obj.id,
                "asset_type": AssetType(item.get("asset_type")),
                "file_url": item.get("file_url"),
                "file_size": item.get("metadata", {}).get("file_size", 0),
                "file_hash": item.get("file_hash")
            }
            
            # Add optional fields only if they exist
            metadata = item.get("metadata", {})
            if "width" in metadata:
                asset_data["width"] = metadata["width"]
            if "height" in metadata:
                asset_data["height"] = metadata["height"]
            if "duration" in metadata:
                asset_data["duration"] = metadata["duration"]
            if "frame_rate" in metadata:
                asset_data["frame_rate"] = metadata["frame_rate"]
            
            asset_obj = TemplateAsset(**asset_data)
            await db.template_assets.insert_one(asset_obj.model_dump())
            
            templates_created.append({
                "template_id": template_obj.id,
                "title": template_obj.title,
                "slug": template_obj.slug,
                "filename": item.get("filename")
            })
            
        except Exception as e:
            errors.append({
                "filename": item.get("filename", "unknown"),
                "error": str(e)
            })
    
    return {
        "templates_created": templates_created,
        "errors": errors,
        "summary": {
            "total_processed": len(import_data.get("items", [])),
            "successful": len(templates_created),
            "failed": len(errors)
        }
    }

# LottieFiles Integration Routes
@api_router.get("/lottiefiles/search")
async def search_lottiefiles_animations(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Animation category"),
    limit: int = Query(20, ge=1, le=100, description="Results per page")
):
    """Search LottieFiles animations with filtering options."""
    try:
        results = await lottiefiles_service.search_animations(query, category, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@api_router.get("/lottiefiles/animation/{animation_id}")
async def get_lottiefiles_animation_details(animation_id: str):
    """Get detailed information about a specific LottieFiles animation."""
    try:
        animation = await lottiefiles_service.get_animation_details(animation_id)
        if not animation:
            raise HTTPException(status_code=404, detail="Animation not found")
        return animation.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get animation details: {str(e)}")

@api_router.get("/lottiefiles/popular")
async def get_popular_lottiefiles_animations(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(6, ge=1, le=50, description="Number of results")
):
    """Get popular LottieFiles animations, optionally filtered by category."""
    try:
        animations = await lottiefiles_service.get_popular_animations(category, limit)
        return animations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get popular animations: {str(e)}")

@api_router.get("/lottiefiles/categories")
async def get_lottiefiles_categories():
    """Get available LottieFiles animation categories."""
    try:
        categories = await lottiefiles_service.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@api_router.get("/lottiefiles/animation/{animation_id}/data")
async def get_lottiefiles_animation_data(animation_id: str):
    """Get the actual Lottie JSON data for an animation."""
    try:
        animation = await lottiefiles_service.get_animation_details(animation_id)
        if not animation:
            raise HTTPException(status_code=404, detail="Animation not found")
        
        # Get the embedded Lottie data
        lottie_data = await lottiefiles_service.download_animation(animation.file_url)
        if not lottie_data:
            raise HTTPException(status_code=404, detail="Animation data not available")
        
        return lottie_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get animation data: {str(e)}")

@api_router.post("/lottiefiles/import/{animation_id}")
async def import_lottiefiles_animation(
    animation_id: str,
    target_category: Optional[str] = Query(None, description="Target category for import")
):
    """Import a LottieFiles animation into the local library."""
    try:
        # Get animation details
        animation = await lottiefiles_service.get_animation_details(animation_id)
        if not animation:
            raise HTTPException(status_code=404, detail="Animation not found")
        
        # Download animation data
        animation_data = await lottiefiles_service.download_animation(animation.file_url)
        if not animation_data:
            raise HTTPException(status_code=400, detail="Failed to download animation data")
        
        # Determine category
        category = target_category or animation.category or "imported"
        
        # Create template from animation
        template_data = {
            "title": animation.name,
            "category": TemplateCategory.MISCELLANEOUS,  # Map to proper category later
            "tags": animation.tags,
            "preview_image_url": animation.thumbnail_url or "https://placeholder.com/400x300",
            "creator_id": "lottiefiles_import",
            "is_public": True,
            "editable_parameters_schema": {
                "canvas": {
                    "width": animation.dimensions.get("width", 400),
                    "height": animation.dimensions.get("height", 400),
                    "background_color": "transparent",
                    "global_playback_speed": 1.0
                },
                "elements": [
                    {
                        "id": "lottie_main",
                        "type": "lottie",
                        "name": animation.name,
                        "parameters": {
                            "source_url": animation.file_url,
                            "loop": True,
                            "autoplay": True,
                            "speed": 1.0,
                            "opacity": 1.0,
                            "x": 50.0,
                            "y": 50.0,
                            "scale": 1.0,
                            "rotation": 0.0
                        }
                    }
                ]
            }
        }
        
        # Map category properly
        category_mapping = {
            "loading": TemplateCategory.ANIMATED_ICONS,
            "success": TemplateCategory.ANIMATED_ICONS,
            "business": TemplateCategory.ADS_PROMOS,
            "technology": TemplateCategory.ADS_PROMOS,
            "education": TemplateCategory.TITLES_QUOTES,
            "social": TemplateCategory.SOCIAL_MEDIA,
            "entertainment": TemplateCategory.MISCELLANEOUS,
            "healthcare": TemplateCategory.ADS_PROMOS,
        }
        template_data["category"] = category_mapping.get(animation.category, TemplateCategory.MISCELLANEOUS)
        
        # Validate and create template
        template_create = TemplateCreate(**template_data)
        validation_errors = validator.validate_editable_parameters(template_create.editable_parameters_schema)
        
        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid template parameters",
                    "errors": validation_errors
                }
            )
        
        # Create slug
        slug = create_slug(template_create.title)
        unique_slug = await ensure_unique_slug(slug)
        
        template_dict = template_create.model_dump()
        template_dict["slug"] = unique_slug
        
        template_obj = Template(**template_dict)
        await db.templates.insert_one(template_obj.model_dump())
        
        # Create template asset record
        import hashlib
        file_hash = hashlib.md5(f"{animation.file_url}_{animation.id}".encode()).hexdigest()
        
        asset_data = {
            "template_id": template_obj.id,
            "asset_type": AssetType.LOTTIE_JSON,
            "file_url": animation.file_url,
            "width": animation.dimensions.get("width"),
            "height": animation.dimensions.get("height"),
            "duration": animation.duration,
            "frame_rate": 30,  # Default for Lottie
            "file_size": animation.file_size or 0,
            "file_hash": file_hash
        }
        
        asset_obj = TemplateAsset(**asset_data)
        await db.template_assets.insert_one(asset_obj.model_dump())
        
        return {
            "message": "Animation imported successfully",
            "template_id": template_obj.id,
            "template_slug": template_obj.slug,
            "template_title": template_obj.title,
            "category": template_obj.category.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)