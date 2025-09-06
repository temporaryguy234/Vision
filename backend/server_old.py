from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'motionedit')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app
app = FastAPI(title="MotionEdit API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums
class TemplateCategory(str, Enum):
    INTROS_OUTROS = "Intros & Outros"
    LOWER_THIRDS = "Lower Thirds"
    TITLES_QUOTES = "Titles & Quotes"
    CHARTS_MAPS = "Charts & Maps"
    SOCIAL_MEDIA = "Social Media Posts"
    ADS_PROMOS = "Ads & Promos"
    OVERLAYS = "Overlays"
    ANIMATED_ICONS = "Animated Icons"
    MISCELLANEOUS = "Miscellaneous"

class ProjectStatus(str, Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class ExportFormat(str, Enum):
    MP4 = "MP4"
    WEBM = "WebM"
    GIF = "GIF"
    LOTTIE_JSON = "Lottie JSON"

class ExportStatus(str, Enum):
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

# Models
class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: TemplateCategory
    preview: str
    tags: List[str] = []
    duration: str
    is_public: bool = True
    creator_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    download_count: int = 0
    rating: float = 0.0
    template_data: Dict[str, Any] = {}

class TemplateCreate(BaseModel):
    title: str
    description: str
    category: TemplateCategory
    preview: str
    tags: List[str] = []
    duration: str
    is_public: bool = True
    template_data: Dict[str, Any] = {}

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    template_id: str
    template_title: str
    thumbnail: str
    status: ProjectStatus
    duration: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    project_data: Dict[str, Any] = {}

class ProjectCreate(BaseModel):
    title: str
    template_id: str
    template_title: str
    thumbnail: str
    status: ProjectStatus = ProjectStatus.DRAFT
    duration: str
    user_id: str
    project_data: Dict[str, Any] = {}

class Export(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    project_name: str
    format: ExportFormat
    resolution: str
    size: str
    duration: str
    status: ExportStatus
    user_id: str
    exported_at: datetime = Field(default_factory=datetime.utcnow)
    download_url: Optional[str] = None
    error_message: Optional[str] = None

class ExportCreate(BaseModel):
    project_id: str
    project_name: str
    format: ExportFormat
    resolution: str
    user_id: str

class BrandKit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    colors: List[str]
    fonts: List[str]
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BrandKitCreate(BaseModel):
    name: str
    description: str
    colors: List[str]
    fonts: List[str]
    user_id: str

class NaturalLanguageCommand(BaseModel):
    command: str
    element_id: Optional[str] = None
    project_id: str

class CommandResult(BaseModel):
    success: bool
    message: str
    changes: Dict[str, Any] = {}
    element_id: Optional[str] = None

# Natural Language Command Parser
class CommandParser:
    def __init__(self):
        self.color_patterns = [
            r'change.*color.*to\s+([#\w]+)',
            r'make.*([#\w]+)',
            r'color.*([#\w]+)',
        ]
        
        self.size_patterns = [
            r'make.*bigger|increase.*size|larger',
            r'make.*smaller|decrease.*size|reduce.*size',
            r'size.*(\d+)',
        ]
        
        self.text_patterns = [
            r'change.*text.*to\s+"([^"]+)"',
            r'text.*"([^"]+)"',
            r'write\s+"([^"]+)"',
        ]
        
        self.position_patterns = [
            r'move.*left|align.*left',
            r'move.*right|align.*right',
            r'move.*center|center.*text',
            r'move.*top',
            r'move.*bottom',
        ]

    def parse_command(self, command: str, element_id: Optional[str] = None) -> CommandResult:
        command_lower = command.lower()
        changes = {}
        
        # Parse color changes
        for pattern in self.color_patterns:
            match = re.search(pattern, command_lower)
            if match:
                color = match.group(1)
                changes['color'] = color
                return CommandResult(
                    success=True,
                    message=f"Changed color to {color}",
                    changes=changes,
                    element_id=element_id
                )
        
        # Parse text changes
        for pattern in self.text_patterns:
            match = re.search(pattern, command_lower)
            if match:
                new_text = match.group(1)
                changes['text'] = new_text
                return CommandResult(
                    success=True,
                    message=f"Changed text to '{new_text}'",
                    changes=changes,
                    element_id=element_id
                )
        
        # Parse size changes
        if 'bigger' in command_lower or 'larger' in command_lower or 'increase' in command_lower:
            changes['fontSize'] = 'increase'
            return CommandResult(
                success=True,
                message="Increased font size",
                changes=changes,
                element_id=element_id
            )
        elif 'smaller' in command_lower or 'reduce' in command_lower or 'decrease' in command_lower:
            changes['fontSize'] = 'decrease'
            return CommandResult(
                success=True,
                message="Decreased font size",
                changes=changes,
                element_id=element_id
            )
        
        # Parse position changes
        if 'left' in command_lower:
            changes['textAlign'] = 'left'
            return CommandResult(
                success=True,
                message="Aligned to left",
                changes=changes,
                element_id=element_id
            )
        elif 'right' in command_lower:
            changes['textAlign'] = 'right'
            return CommandResult(
                success=True,
                message="Aligned to right",
                changes=changes,
                element_id=element_id
            )
        elif 'center' in command_lower:
            changes['textAlign'] = 'center'
            return CommandResult(
                success=True,
                message="Centered text",
                changes=changes,
                element_id=element_id
            )
        
        return CommandResult(
            success=False,
            message="Command not recognized. Try commands like 'change color to red', 'make text bigger', or 'change text to \"Hello World\"'"
        )

# Initialize command parser
command_parser = CommandParser()

# Routes
@api_router.get("/")
async def root():
    return {"message": "MotionEdit API", "version": "1.0.0"}

# Template Routes
@api_router.get("/templates", response_model=List[Template])
async def get_templates(
    category: Optional[TemplateCategory] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get templates with optional filtering"""
    query = {}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    templates = await db.templates.find(query).skip(skip).limit(limit).to_list(limit)
    return [Template(**template) for template in templates]

@api_router.post("/templates", response_model=Template)
async def create_template(template: TemplateCreate):
    """Create a new template"""
    template_dict = template.dict()
    template_obj = Template(**template_dict)
    
    await db.templates.insert_one(template_obj.dict())
    return template_obj

@api_router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get a specific template"""
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return Template(**template)

@api_router.put("/templates/{template_id}", response_model=Template)
async def update_template(template_id: str, template_update: TemplateCreate):
    """Update a template"""
    update_data = template_update.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    
    updated_template = await db.templates.find_one({"id": template_id})
    return Template(**updated_template)

# Project Routes
@api_router.get("/projects", response_model=List[Project])
async def get_projects(
    user_id: str,
    status: Optional[ProjectStatus] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user projects"""
    query = {"user_id": user_id}
    
    if status:
        query["status"] = status
    
    projects = await db.projects.find(query).skip(skip).limit(limit).to_list(limit)
    return [Project(**project) for project in projects]

@api_router.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate):
    """Create a new project"""
    project_dict = project.dict()
    project_obj = Project(**project_dict)
    
    await db.projects.insert_one(project_obj.dict())
    return project_obj

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project"""
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project_data: Dict[str, Any]):
    """Update project data"""
    update_data = {
        "project_data": project_data,
        "updated_at": datetime.utcnow()
    }
    
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

# Natural Language Command Routes
@api_router.post("/commands/parse", response_model=CommandResult)
async def parse_command(command_data: NaturalLanguageCommand):
    """Parse and execute natural language command"""
    result = command_parser.parse_command(
        command_data.command, 
        command_data.element_id
    )
    
    # If successful, you could also update the project data here
    if result.success and command_data.project_id:
        # Update project with the changes
        await db.projects.update_one(
            {"id": command_data.project_id},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
    
    return result

# Export Routes
@api_router.get("/exports", response_model=List[Export])
async def get_exports(
    user_id: str,
    status: Optional[ExportStatus] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user exports"""
    query = {"user_id": user_id}
    
    if status:
        query["status"] = status
    
    exports = await db.exports.find(query).skip(skip).limit(limit).to_list(limit)
    return [Export(**export) for export in exports]

@api_router.post("/exports", response_model=Export)
async def create_export(export_data: ExportCreate):
    """Create a new export job"""
    export_dict = export_data.dict()
    
    # Simulate export processing
    export_dict.update({
        "size": "45.2 MB",  # This would be calculated during actual export
        "duration": "15s",   # This would come from project data
        "status": ExportStatus.PROCESSING,
        "download_url": None
    })
    
    export_obj = Export(**export_dict)
    await db.exports.insert_one(export_obj.dict())
    
    # In a real implementation, you would start background export processing here
    
    return export_obj

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
    brand_kit_dict = brand_kit.dict()
    brand_kit_obj = BrandKit(**brand_kit_dict)
    
    await db.brand_kits.insert_one(brand_kit_obj.dict())
    return brand_kit_obj

@api_router.delete("/brand-kits/{kit_id}")
async def delete_brand_kit(kit_id: str):
    """Delete a brand kit"""
    result = await db.brand_kits.delete_one({"id": kit_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return {"message": "Brand kit deleted successfully"}

# Statistics Routes
@api_router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    template_count = await db.templates.count_documents({})
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

# File Upload Routes
@api_router.post("/upload/template")
async def upload_template(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    category: TemplateCategory = Form(...),
    tags: str = Form(...)
):
    """Upload a new template file"""
    # In a real implementation, you would:
    # 1. Validate file type and size
    # 2. Process the file (extract preview, analyze structure)
    # 3. Store file in cloud storage
    # 4. Create template record in database
    
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    template_data = TemplateCreate(
        title=title,
        description=description,
        category=category,
        tags=tag_list,
        preview=f"https://placeholder.com/300x200",  # Would be actual preview URL
        duration="5s",  # Would be extracted from file
        template_data={"original_filename": file.filename}
    )
    
    return await create_template(template_data)

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)