from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re
import uuid

# Import our models and file storage
from models import *
from file_storage import file_storage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'motionedit')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app
app = FastAPI(
    title="MotionEdit API",
    version="2.0.0",
    description="Comprehensive Motion Graphics Template Platform API"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=['*'],  # Allow all origins for development
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(exist_ok=True, parents=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions
def create_slug(title: str) -> str:
    """Create a URL-friendly slug from title"""
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

async def ensure_unique_slug(slug: str, template_id: Optional[str] = None) -> str:
    """Ensure slug is unique by appending numbers if necessary"""
    original_slug = slug
    counter = 1
    
    while True:
        query = {"slug": slug}
        if template_id:
            query["id"] = {"$ne": template_id}
            
        existing = await db.templates.find_one(query)
        if not existing:
            return slug
            
        slug = f"{original_slug}-{counter}"
        counter += 1

# Validation functions for editable parameters
class ParametersValidator:
    @staticmethod
    def validate_editable_parameters(schema: EditableParametersSchema) -> Dict[str, str]:
        """Validate editable parameters schema and return errors"""
        errors = {}
        
        try:
            # Validate canvas parameters
            canvas = schema.canvas
            if canvas.width < 100 or canvas.width > 4000:
                errors['canvas.width'] = "Width must be between 100 and 4000 pixels"
            if canvas.height < 100 or canvas.height > 4000:
                errors['canvas.height'] = "Height must be between 100 and 4000 pixels"
            if canvas.global_playback_speed < 0.5 or canvas.global_playback_speed > 2.0:
                errors['canvas.global_playback_speed'] = "Playback speed must be between 0.5× and 2.0×"
            
            # Validate background color
            if canvas.background_color != "transparent":
                if not re.match(r'^#[0-9A-Fa-f]{6}$', canvas.background_color):
                    errors['canvas.background_color'] = "Background color must be a valid hex color or 'transparent'"
            
            # Validate elements
            element_ids = set()
            for i, element in enumerate(schema.elements):
                element_prefix = f"elements[{i}]"
                
                # Check for duplicate IDs
                if element.id in element_ids:
                    errors[f"{element_prefix}.id"] = f"Duplicate element ID: {element.id}"
                element_ids.add(element.id)
                
                # Validate parameters based on element type
                params = element.parameters
                
                if element.type == ElementType.TEXT:
                    if len(params.content) > 500:
                        errors[f"{element_prefix}.content"] = "Text content must not exceed 500 characters"
                    if params.font_size < 12 or params.font_size > 180:
                        errors[f"{element_prefix}.font_size"] = "Font size must be between 12 and 180 pixels"
                
                elif element.type == ElementType.CHART:
                    if params.line_width < 0 or params.line_width > 20:
                        errors[f"{element_prefix}.line_width"] = "Line width must be between 0 and 20 pixels"
                    if params.bar_width < 1 or params.bar_width > 40:
                        errors[f"{element_prefix}.bar_width"] = "Bar width must be between 1 and 40 pixels"
                
                elif element.type == ElementType.SHAPE:
                    if params.stroke_width < 0 or params.stroke_width > 20:
                        errors[f"{element_prefix}.stroke_width"] = "Stroke width must be between 0 and 20 pixels"
                
                elif element.type == ElementType.MAP:
                    if params.border_width < 0 or params.border_width > 12:
                        errors[f"{element_prefix}.border_width"] = "Border width must be between 0 and 12 pixels"
                
                # Validate common parameters (position, scale, rotation, opacity)
                if hasattr(params, 'x') and (params.x < 0 or params.x > 100):
                    errors[f"{element_prefix}.x"] = "X position must be between 0 and 100 percent"
                if hasattr(params, 'y') and (params.y < 0 or params.y > 100):
                    errors[f"{element_prefix}.y"] = "Y position must be between 0 and 100 percent"
                if hasattr(params, 'scale') and (params.scale < 0.1 or params.scale > 5.0):
                    errors[f"{element_prefix}.scale"] = "Scale must be between 0.1 and 5.0"
                if hasattr(params, 'rotation') and (params.rotation < -360 or params.rotation > 360):
                    errors[f"{element_prefix}.rotation"] = "Rotation must be between -360 and 360 degrees"
                if hasattr(params, 'opacity') and (params.opacity < 0 or params.opacity > 1):
                    errors[f"{element_prefix}.opacity"] = "Opacity must be between 0 and 1"
                
                # Validate entrance animation if present
                if hasattr(params, 'entrance_animation') and params.entrance_animation:
                    anim = params.entrance_animation
                    if anim.delay < 0 or anim.delay > 5:
                        errors[f"{element_prefix}.entrance_animation.delay"] = "Animation delay must be between 0 and 5 seconds"
                    if anim.duration < 0.5 or anim.duration > 5:
                        errors[f"{element_prefix}.entrance_animation.duration"] = "Animation duration must be between 0.5 and 5 seconds"
        
        except Exception as e:
            errors['schema'] = f"Invalid schema structure: {str(e)}"
        
        return errors

validator = ParametersValidator()

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

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)