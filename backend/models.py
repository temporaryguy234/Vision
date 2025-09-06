from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
import uuid

# Enums for consistent data types
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

class AssetType(str, Enum):
    LOTTIE_JSON = "Lottie JSON"
    MP4 = "MP4"
    WEBM_ALPHA = "WebM with Alpha"
    GIF = "GIF"
    PNG = "PNG"
    SVG = "SVG"

class AspectRatio(str, Enum):
    WIDESCREEN = "16:9"
    VERTICAL = "9:16"
    SQUARE = "1:1"
    FOUR_FIVE = "4:5"
    CUSTOM = "custom"

class ProjectStatus(str, Enum):
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class ExportFormat(str, Enum):
    MP4 = "MP4"
    GIF = "GIF"
    WEBM_ALPHA = "WebM with Alpha"
    LOTTIE_JSON = "Lottie JSON"

class ExportResolution(str, Enum):
    FOUR_K = "4K"
    FULL_HD = "1080p"
    HD = "720p"
    CUSTOM = "custom"

class ExportStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    DONE = "done"
    FAILED = "failed"

class ElementType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    SHAPE = "shape"
    CHART = "chart"
    MAP = "map"
    LOTTIE = "lottie"

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"

class AnimationType(str, Enum):
    FLY_IN_LEFT = "fly-in-left"
    FLY_IN_RIGHT = "fly-in-right"
    FLY_IN_TOP = "fly-in-top"
    FLY_IN_BOTTOM = "fly-in-bottom"
    FADE_IN = "fade-in"
    SCALE_IN = "scale-in"
    BOUNCE_IN = "bounce-in"

class EasingType(str, Enum):
    EASE = "ease"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    LINEAR = "linear"

# Editable Parameters Schema Models
class CanvasParameters(BaseModel):
    width: int = Field(ge=100, le=4000, description="Canvas width in pixels")
    height: int = Field(ge=100, le=4000, description="Canvas height in pixels")
    background_color: Optional[str] = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$|^transparent$")
    global_playback_speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Global playback speed multiplier")

class EntranceAnimation(BaseModel):
    type: AnimationType
    delay: float = Field(default=0.0, ge=0.0, le=5.0, description="Animation delay in seconds")
    duration: float = Field(default=1.0, ge=0.5, le=5.0, description="Animation duration in seconds")
    easing: EasingType = EasingType.EASE

class TextElementParameters(BaseModel):
    content: str = Field(max_length=500, description="Text content")
    font_family: str = Field(default="Inter", description="Font family name")
    font_size: int = Field(default=24, ge=12, le=180, description="Font size in pixels")
    color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    alignment: str = Field(default="center", pattern=r"^(left|center|right)$")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    x: float = Field(default=50.0, ge=0.0, le=100.0, description="X position as percentage")
    y: float = Field(default=50.0, ge=0.0, le=100.0, description="Y position as percentage")
    scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Scale multiplier")
    rotation: float = Field(default=0.0, ge=-360.0, le=360.0, description="Rotation in degrees")
    entrance_animation: Optional[EntranceAnimation] = None

class ImageElementParameters(BaseModel):
    source_url: Optional[str] = Field(description="Image source URL")
    fit: str = Field(default="cover", pattern=r"^(cover|contain)$")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    x: float = Field(default=50.0, ge=0.0, le=100.0, description="X position as percentage")
    y: float = Field(default=50.0, ge=0.0, le=100.0, description="Y position as percentage")
    scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Scale multiplier")
    rotation: float = Field(default=0.0, ge=-360.0, le=360.0, description="Rotation in degrees")
    entrance_animation: Optional[EntranceAnimation] = None

class ShapeElementParameters(BaseModel):
    fill_color: str = Field(default="#0000FF", pattern=r"^#[0-9A-Fa-f]{6}$")
    stroke_color: Optional[str] = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    stroke_width: int = Field(default=0, ge=0, le=20, description="Stroke width in pixels")
    corner_radius: int = Field(default=0, ge=0, le=100, description="Corner radius in pixels")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    x: float = Field(default=50.0, ge=0.0, le=100.0, description="X position as percentage")
    y: float = Field(default=50.0, ge=0.0, le=100.0, description="Y position as percentage")
    scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Scale multiplier")
    rotation: float = Field(default=0.0, ge=-360.0, le=360.0, description="Rotation in degrees")
    entrance_animation: Optional[EntranceAnimation] = None

class ChartElementParameters(BaseModel):
    chart_type: ChartType = ChartType.BAR
    series_colors: List[str] = Field(default=["#3B82F6", "#EF4444", "#10B981"], description="Chart colors")
    show_labels: bool = Field(default=True)
    line_width: int = Field(default=2, ge=0, le=20, description="Line width for line charts")
    bar_width: int = Field(default=20, ge=1, le=40, description="Bar width for bar charts")
    data_placeholder: List[float] = Field(default=[10, 20, 30, 40], description="Sample data for chart")
    x: float = Field(default=50.0, ge=0.0, le=100.0, description="X position as percentage")
    y: float = Field(default=50.0, ge=0.0, le=100.0, description="Y position as percentage")
    scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Scale multiplier")
    entrance_animation: Optional[EntranceAnimation] = None

    @validator('series_colors')
    def validate_colors(cls, v):
        import re
        for color in v:
            if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
                raise ValueError(f"Invalid color format: {color}")
        return v

class MapElementParameters(BaseModel):
    focus_region: str = Field(default="world", description="Geographic focus (world, country code, region)")
    land_color: str = Field(default="#10B981", pattern=r"^#[0-9A-Fa-f]{6}$")
    border_color: str = Field(default="#374151", pattern=r"^#[0-9A-Fa-f]{6}$")
    border_width: int = Field(default=1, ge=0, le=12, description="Border width in pixels")
    show_labels: bool = Field(default=True)
    x: float = Field(default=50.0, ge=0.0, le=100.0, description="X position as percentage")
    y: float = Field(default=50.0, ge=0.0, le=100.0, description="Y position as percentage")
    scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Scale multiplier")
    entrance_animation: Optional[EntranceAnimation] = None

class LottieElementParameters(BaseModel):
    source_url: Optional[str] = Field(description="Lottie JSON file URL")
    loop: bool = Field(default=True, description="Loop animation")
    autoplay: bool = Field(default=True, description="Autoplay animation")
    speed: float = Field(default=1.0, ge=0.1, le=5.0, description="Animation speed multiplier")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0)
    x: float = Field(default=50.0, ge=0.0, le=100.0, description="X position as percentage")
    y: float = Field(default=50.0, ge=0.0, le=100.0, description="Y position as percentage")
    scale: float = Field(default=1.0, ge=0.1, le=5.0, description="Scale multiplier")
    rotation: float = Field(default=0.0, ge=-360.0, le=360.0, description="Rotation in degrees")
    entrance_animation: Optional[EntranceAnimation] = None

class EditableElement(BaseModel):
    id: str
    type: ElementType
    name: str
    parameters: Union[
        TextElementParameters,
        ImageElementParameters, 
        ShapeElementParameters,
        ChartElementParameters,
        MapElementParameters,
        LottieElementParameters
    ]

class EditableParametersSchema(BaseModel):
    canvas: CanvasParameters
    elements: List[EditableElement]

# Main Database Models
class Template(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=200, description="URL-friendly version of title")
    category: TemplateCategory
    tags: List[str] = Field(default=[])
    preview_image_url: str = Field(description="URL to preview image")
    supported_aspect_ratios: List[AspectRatio] = Field(default=[AspectRatio.WIDESCREEN])
    editable_parameters_schema: EditableParametersSchema
    creator_id: str = Field(description="ID of the template creator")
    version: str = Field(default="1.0.0", description="Template version")
    is_public: bool = Field(default=True)
    download_count: int = Field(default=0, ge=0)
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('slug')
    def validate_slug(cls, v):
        import re
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return v

class TemplateAsset(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = Field(description="Reference to parent template")
    asset_type: AssetType
    file_url: str = Field(description="Public URL to the asset file")
    width: Optional[int] = Field(ge=1, description="Asset width in pixels")
    height: Optional[int] = Field(ge=1, description="Asset height in pixels")
    duration: Optional[float] = Field(ge=0.0, description="Duration in seconds for video/animation assets")
    frame_rate: Optional[int] = Field(ge=1, le=120, description="Frame rate for video assets")
    file_size: int = Field(ge=0, description="File size in bytes")
    file_hash: Optional[str] = Field(description="MD5 hash for duplicate detection")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="ID of the project owner")
    template_id: str = Field(description="Reference to source template")
    title: str = Field(min_length=1, max_length=200)
    status: ProjectStatus = ProjectStatus.DRAFT
    current_editor_state: Dict[str, Any] = Field(default={}, description="User's current edits and modifications")
    thumbnail_url: Optional[str] = Field(description="Generated thumbnail for the project")
    duration: Optional[float] = Field(ge=0.0, description="Project duration in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BrandKit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="ID of the brand kit owner")
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(max_length=500)
    colors: List[str] = Field(default=[], description="Brand colors in hex format")
    fonts: List[str] = Field(default=[], description="Brand font families")
    logo_urls: List[str] = Field(default=[], description="URLs to brand logos")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('colors')
    def validate_colors(cls, v):
        import re
        for color in v:
            if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
                raise ValueError(f"Invalid color format: {color}")
        return v

class Export(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(description="ID of the export owner")
    project_id: str = Field(description="Reference to source project")
    format: ExportFormat
    resolution: ExportResolution
    aspect_ratio: AspectRatio
    custom_width: Optional[int] = Field(ge=100, le=4000, description="Custom width for custom resolution")
    custom_height: Optional[int] = Field(ge=100, le=4000, description="Custom height for custom resolution")
    fps: int = Field(default=30, ge=1, le=120, description="Frames per second")
    transparent_background: bool = Field(default=False, description="Enable transparent background")
    status: ExportStatus = ExportStatus.QUEUED
    progress: int = Field(default=0, ge=0, le=100, description="Export progress percentage")
    download_url: Optional[str] = Field(description="URL to download the exported file")
    file_size: Optional[int] = Field(ge=0, description="Final file size in bytes")
    error_message: Optional[str] = Field(description="Error message if export failed")
    estimated_duration: Optional[int] = Field(ge=0, description="Estimated render time in seconds")
    actual_duration: Optional[int] = Field(ge=0, description="Actual render time in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(description="Timestamp when export completed")

# Request/Response Models for API
class TemplateCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: TemplateCategory
    tags: List[str] = Field(default=[])
    preview_image_url: str
    supported_aspect_ratios: List[AspectRatio] = Field(default=[AspectRatio.WIDESCREEN])
    editable_parameters_schema: EditableParametersSchema
    creator_id: str
    version: str = Field(default="1.0.0")
    is_public: bool = Field(default=True)

class TemplateUpdate(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=200)
    category: Optional[TemplateCategory]
    tags: Optional[List[str]]
    preview_image_url: Optional[str]
    supported_aspect_ratios: Optional[List[AspectRatio]]
    editable_parameters_schema: Optional[EditableParametersSchema]
    version: Optional[str]
    is_public: Optional[bool]

class TemplateAssetCreate(BaseModel):
    template_id: str
    asset_type: AssetType
    file_url: str
    width: Optional[int] = Field(ge=1)
    height: Optional[int] = Field(ge=1)
    duration: Optional[float] = Field(ge=0.0)
    frame_rate: Optional[int] = Field(ge=1, le=120)
    file_size: int = Field(ge=0)
    file_hash: Optional[str]

class ProjectCreate(BaseModel):
    template_id: str
    title: str = Field(min_length=1, max_length=200)
    user_id: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(min_length=1, max_length=200)
    status: Optional[ProjectStatus]
    current_editor_state: Optional[Dict[str, Any]]
    thumbnail_url: Optional[str]
    duration: Optional[float] = Field(ge=0.0)

class BrandKitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(max_length=500)
    colors: List[str] = Field(default=[])
    fonts: List[str] = Field(default=[])
    logo_urls: List[str] = Field(default=[])
    user_id: str

class BrandKitUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(max_length=500)
    colors: Optional[List[str]]
    fonts: Optional[List[str]]
    logo_urls: Optional[List[str]]

class ExportCreate(BaseModel):
    project_id: str
    user_id: str
    format: ExportFormat
    resolution: ExportResolution = ExportResolution.FULL_HD
    aspect_ratio: AspectRatio = AspectRatio.WIDESCREEN
    custom_width: Optional[int] = Field(ge=100, le=4000)
    custom_height: Optional[int] = Field(ge=100, le=4000)
    fps: int = Field(default=30, ge=1, le=120)
    transparent_background: bool = Field(default=False)