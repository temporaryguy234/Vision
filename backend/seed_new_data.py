import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from models import *

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'motionedit')

async def seed_database():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Clear existing data
    await db.templates.delete_many({})
    await db.template_assets.delete_many({})
    await db.projects.delete_many({})
    await db.brand_kits.delete_many({})
    await db.exports.delete_many({})
    
    print("🧹 Cleared existing data")
    
    # Create comprehensive editable parameters schemas
    modern_intro_schema = EditableParametersSchema(
        canvas=CanvasParameters(
            width=1920,
            height=1080,
            background_color="transparent",
            global_playback_speed=1.0
        ),
        elements=[
            EditableElement(
                id="main_title",
                type=ElementType.TEXT,
                name="Main Title",
                parameters=TextElementParameters(
                    content="Your Brand",
                    font_family="Inter",
                    font_size=48,
                    color="#FFFFFF",
                    alignment="center",
                    x=50.0,
                    y=30.0,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.FADE_IN,
                        delay=0.5,
                        duration=1.0,
                        easing=EasingType.EASE_OUT
                    )
                )
            ),
            EditableElement(
                id="subtitle",
                type=ElementType.TEXT,
                name="Subtitle",
                parameters=TextElementParameters(
                    content="Professional Content",
                    font_family="Inter",
                    font_size=24,
                    color="#E5E7EB",
                    alignment="center",
                    x=50.0,
                    y=60.0,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.FLY_IN_BOTTOM,
                        delay=1.0,
                        duration=0.8,
                        easing=EasingType.EASE_OUT
                    )
                )
            ),
            EditableElement(
                id="logo",
                type=ElementType.IMAGE,
                name="Logo",
                parameters=ImageElementParameters(
                    source_url="https://placeholder.com/200x200",
                    fit="contain",
                    x=50.0,
                    y=80.0,
                    scale=0.5,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.SCALE_IN,
                        delay=1.5,
                        duration=0.6,
                        easing=EasingType.EASE_OUT
                    )
                )
            )
        ]
    )
    
    chart_animation_schema = EditableParametersSchema(
        canvas=CanvasParameters(
            width=1920,
            height=1080,
            background_color="#1F2937",
            global_playback_speed=1.0
        ),
        elements=[
            EditableElement(
                id="chart_title",
                type=ElementType.TEXT,
                name="Chart Title",
                parameters=TextElementParameters(
                    content="Sales Report Q4",
                    font_family="Roboto",
                    font_size=36,
                    color="#FFFFFF",
                    alignment="center",
                    x=50.0,
                    y=15.0
                )
            ),
            EditableElement(
                id="main_chart",
                type=ElementType.CHART,
                name="Bar Chart",
                parameters=ChartElementParameters(
                    chart_type=ChartType.BAR,
                    series_colors=["#3B82F6", "#EF4444", "#10B981", "#F59E0B"],
                    show_labels=True,
                    bar_width=25,
                    data_placeholder=[45, 67, 89, 102, 78, 93],
                    x=50.0,
                    y=55.0,
                    scale=1.0,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.FLY_IN_LEFT,
                        delay=0.8,
                        duration=1.2,
                        easing=EasingType.EASE_OUT
                    )
                )
            )
        ]
    )
    
    logo_reveal_schema = EditableParametersSchema(
        canvas=CanvasParameters(
            width=1080,
            height=1080,
            background_color="#000000",
            global_playback_speed=1.0
        ),
        elements=[
            EditableElement(
                id="background_shape",
                type=ElementType.SHAPE,
                name="Background Circle",
                parameters=ShapeElementParameters(
                    fill_color="#FF6B35",
                    stroke_color="#FFFFFF",
                    stroke_width=3,
                    corner_radius=50,
                    x=50.0,
                    y=50.0,
                    scale=0.8,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.SCALE_IN,
                        delay=0.0,
                        duration=0.8,
                        easing=EasingType.EASE_OUT
                    )
                )
            ),
            EditableElement(
                id="company_logo",
                type=ElementType.IMAGE,
                name="Company Logo",
                parameters=ImageElementParameters(
                    source_url="https://placeholder.com/300x300",
                    fit="contain",
                    x=50.0,
                    y=50.0,
                    scale=0.6,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.FADE_IN,
                        delay=1.0,
                        duration=1.0,
                        easing=EasingType.EASE
                    )
                )
            )
        ]
    )
    
    quote_typography_schema = EditableParametersSchema(
        canvas=CanvasParameters(
            width=1080,
            height=1350,
            background_color="#F3F4F6",
            global_playback_speed=1.0
        ),
        elements=[
            EditableElement(
                id="quote_text",
                type=ElementType.TEXT,
                name="Quote",
                parameters=TextElementParameters(
                    content="\"Dream big, work hard, stay focused\"",
                    font_family="Montserrat",
                    font_size=42,
                    color="#1F2937",
                    alignment="center",
                    x=50.0,
                    y=40.0,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.FADE_IN,
                        delay=0.5,
                        duration=1.5,
                        easing=EasingType.EASE_OUT
                    )
                )
            ),
            EditableElement(
                id="author",
                type=ElementType.TEXT,
                name="Author",
                parameters=TextElementParameters(
                    content="- Motivational Quote",
                    font_family="Montserrat",
                    font_size=20,
                    color="#6B7280",
                    alignment="center",
                    x=50.0,
                    y=65.0,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.FLY_IN_BOTTOM,
                        delay=2.0,
                        duration=0.8,
                        easing=EasingType.EASE_OUT
                    )
                )
            )
        ]
    )
    
    world_map_schema = EditableParametersSchema(
        canvas=CanvasParameters(
            width=1920,
            height=1080,
            background_color="#0F1419",
            global_playback_speed=1.0
        ),
        elements=[
            EditableElement(
                id="map_title",
                type=ElementType.TEXT,
                name="Map Title",
                parameters=TextElementParameters(
                    content="Global Statistics 2024",
                    font_family="Inter",
                    font_size=32,
                    color="#FFFFFF",
                    alignment="center",
                    x=50.0,
                    y=10.0
                )
            ),
            EditableElement(
                id="world_map",
                type=ElementType.MAP,
                name="World Map",
                parameters=MapElementParameters(
                    focus_region="world",
                    land_color="#10B981",
                    border_color="#374151",
                    border_width=1,
                    show_labels=True,
                    x=50.0,
                    y=55.0,
                    scale=1.0,
                    entrance_animation=EntranceAnimation(
                        type=AnimationType.SCALE_IN,
                        delay=0.5,
                        duration=1.0,
                        easing=EasingType.EASE_OUT
                    )
                )
            )
        ]
    )
    
    # Seed Templates with comprehensive data
    templates = [
        Template(
            id="template_001",
            title="Modern Social Media Intro",
            slug="modern-social-media-intro",
            category=TemplateCategory.INTROS_OUTROS,
            tags=["Instagram", "TikTok", "Modern", "Trendy", "Social"],
            preview_image_url="https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop",
            supported_aspect_ratios=[AspectRatio.WIDESCREEN, AspectRatio.SQUARE],
            editable_parameters_schema=modern_intro_schema,
            creator_id="admin_001",
            version="1.2.0",
            is_public=True,
            download_count=1580,
            rating=4.8
        ),
        Template(
            id="template_002",
            title="Animated Data Chart",
            slug="animated-data-chart",
            category=TemplateCategory.CHARTS_MAPS,
            tags=["Chart", "Analytics", "Business", "Professional", "Data"],
            preview_image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
            supported_aspect_ratios=[AspectRatio.WIDESCREEN],
            editable_parameters_schema=chart_animation_schema,
            creator_id="admin_001",
            version="1.0.0",
            is_public=True,
            download_count=920,
            rating=4.6
        ),
        Template(
            id="template_003",
            title="Logo Reveal Animation",
            slug="logo-reveal-animation",
            category=TemplateCategory.ANIMATED_ICONS,
            tags=["Logo", "Branding", "Corporate", "Clean", "Reveal"],
            preview_image_url="https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400&h=300&fit=crop",
            supported_aspect_ratios=[AspectRatio.SQUARE],
            editable_parameters_schema=logo_reveal_schema,
            creator_id="admin_001",
            version="1.1.0",
            is_public=True,
            download_count=2340,
            rating=4.9
        ),
        Template(
            id="template_004",
            title="Inspirational Quote Typography",
            slug="inspirational-quote-typography",
            category=TemplateCategory.TITLES_QUOTES,
            tags=["Typography", "Motivational", "Social", "Elegant", "Quote"],
            preview_image_url="https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=400&h=300&fit=crop",
            supported_aspect_ratios=[AspectRatio.VERTICAL, AspectRatio.FOUR_FIVE],
            editable_parameters_schema=quote_typography_schema,
            creator_id="admin_001",
            version="1.0.0",
            is_public=True,
            download_count=1750,
            rating=4.7
        ),
        Template(
            id="template_005",
            title="World Map Data Visualization",
            slug="world-map-data-visualization",
            category=TemplateCategory.CHARTS_MAPS,
            tags=["Map", "Global", "Data", "Infographic", "Statistics"],
            preview_image_url="https://images.unsplash.com/photo-1597149961283-62c2e52b98d6?w=400&h=300&fit=crop",
            supported_aspect_ratios=[AspectRatio.WIDESCREEN],
            editable_parameters_schema=world_map_schema,
            creator_id="admin_001",
            version="1.0.0",
            is_public=True,
            download_count=1120,
            rating=4.5
        )
    ]
    
    # Insert templates
    for template in templates:
        await db.templates.insert_one(template.dict())
    
    print(f"✅ Seeded {len(templates)} templates with comprehensive schemas")
    
    # Seed Template Assets
    template_assets = [
        # Assets for Modern Social Media Intro
        TemplateAsset(
            id="asset_001",
            template_id="template_001",
            asset_type=AssetType.LOTTIE_JSON,
            file_url="/uploads/lottie/template_001/intro-animation.json",
            width=1920,
            height=1080,
            duration=5.0,
            frame_rate=30,
            file_size=125000
        ),
        TemplateAsset(
            id="asset_002",
            template_id="template_001",
            asset_type=AssetType.MP4,
            file_url="/uploads/videos/mp4/template_001/preview.mp4",
            width=1920,
            height=1080,
            duration=5.0,
            frame_rate=30,
            file_size=2500000
        ),
        
        # Assets for Animated Data Chart
        TemplateAsset(
            id="asset_003",
            template_id="template_002",
            asset_type=AssetType.LOTTIE_JSON,
            file_url="/uploads/lottie/template_002/chart-animation.json",
            width=1920,
            height=1080,
            duration=8.0,
            frame_rate=30,
            file_size=180000
        ),
        
        # Assets for Logo Reveal
        TemplateAsset(
            id="asset_004",
            template_id="template_003",
            asset_type=AssetType.LOTTIE_JSON,
            file_url="/uploads/lottie/template_003/logo-reveal.json",
            width=1080,
            height=1080,
            duration=3.0,
            frame_rate=30,
            file_size=95000
        ),
        TemplateAsset(
            id="asset_005",
            template_id="template_003",
            asset_type=AssetType.PNG,
            file_url="/uploads/images/png/template_003/logo-placeholder.png",
            width=300,
            height=300,
            file_size=45000
        ),
        
        # Assets for Quote Typography
        TemplateAsset(
            id="asset_006",
            template_id="template_004",
            asset_type=AssetType.LOTTIE_JSON,
            file_url="/uploads/lottie/template_004/quote-animation.json",
            width=1080,
            height=1350,
            duration=6.0,
            frame_rate=30,
            file_size=110000
        ),
        
        # Assets for World Map
        TemplateAsset(
            id="asset_007",
            template_id="template_005",
            asset_type=AssetType.LOTTIE_JSON,
            file_url="/uploads/lottie/template_005/world-map.json",
            width=1920,
            height=1080,
            duration=7.0,
            frame_rate=30,
            file_size=220000
        )
    ]
    
    # Insert template assets
    for asset in template_assets:
        await db.template_assets.insert_one(asset.dict())
    
    print(f"✅ Seeded {len(template_assets)} template assets")
    
    # Seed Sample Projects
    projects = [
        Project(
            id="project_001",
            user_id="user_001",
            template_id="template_001",
            title="Summer Marketing Campaign",
            status=ProjectStatus.IN_PROGRESS,
            current_editor_state={
                "canvas": {
                    "width": 1920,
                    "height": 1080,
                    "background_color": "transparent",
                    "global_playback_speed": 1.0
                },
                "elements": {
                    "main_title": {
                        "content": "Summer Sale 2024",
                        "color": "#FF6B35",
                        "font_size": 52
                    },
                    "subtitle": {
                        "content": "Up to 50% Off Everything",
                        "color": "#FFFFFF"
                    }
                }
            },
            thumbnail_url="https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=300&h=200&fit=crop",
            duration=5.0
        ),
        Project(
            id="project_002",
            user_id="user_001",
            template_id="template_002",
            title="Q4 Sales Performance Report",
            status=ProjectStatus.COMPLETED,
            current_editor_state={
                "canvas": {
                    "width": 1920,
                    "height": 1080,
                    "background_color": "#1F2937",
                    "global_playback_speed": 1.0
                },
                "elements": {
                    "chart_title": {
                        "content": "Q4 2024 Sales Performance"
                    },
                    "main_chart": {
                        "chart_type": "bar",
                        "data_placeholder": [120, 150, 180, 200, 165, 195],
                        "series_colors": ["#3B82F6", "#10B981", "#F59E0B"]
                    }
                }
            },
            thumbnail_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop",
            duration=8.0
        ),
        Project(
            id="project_003",
            user_id="user_002",
            template_id="template_003",
            title="TechCorp Brand Reveal",
            status=ProjectStatus.DRAFT,
            current_editor_state={
                "canvas": {
                    "width": 1080,
                    "height": 1080,
                    "background_color": "#000000",
                    "global_playback_speed": 1.2
                },
                "elements": {
                    "company_logo": {
                        "source_url": "https://placeholder.com/techcorp-logo.png"
                    },
                    "background_shape": {
                        "fill_color": "#3B82F6"
                    }
                }
            },
            thumbnail_url="https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=300&h=200&fit=crop",
            duration=3.0
        )
    ]
    
    # Insert projects
    for project in projects:
        await db.projects.insert_one(project.dict())
    
    print(f"✅ Seeded {len(projects)} projects")
    
    # Seed Brand Kits
    brand_kits = [
        BrandKit(
            id="brandkit_001",
            user_id="user_001",
            name="Corporate Blue",
            description="Professional and trustworthy brand colors for corporate presentations",
            colors=["#1E40AF", "#3B82F6", "#60A5FA", "#93C5FD", "#DBEAFE"],
            fonts=["Inter", "Roboto", "Open Sans"],
            logo_urls=["https://placeholder.com/logo-corporate.png"]
        ),
        BrandKit(
            id="brandkit_002",
            user_id="user_001",
            name="Sunset Gradient",
            description="Warm and energetic brand palette perfect for creative agencies",
            colors=["#EA580C", "#F97316", "#FB923C", "#FDBA74", "#FED7AA"],
            fonts=["Poppins", "Montserrat", "Nunito"],
            logo_urls=["https://placeholder.com/logo-sunset.png"]
        ),
        BrandKit(
            id="brandkit_003",
            user_id="user_002",
            name="Nature Green",
            description="Fresh and organic color scheme for eco-friendly brands",
            colors=["#059669", "#10B981", "#34D399", "#6EE7B7", "#A7F3D0"],
            fonts=["Lato", "Source Sans Pro", "Ubuntu"],
            logo_urls=["https://placeholder.com/logo-nature.png", "https://placeholder.com/logo-nature-alt.png"]
        ),
        BrandKit(
            id="brandkit_004",
            user_id="user_002",
            name="Royal Purple",
            description="Elegant and premium brand colors for luxury brands",
            colors=["#7C3AED", "#8B5CF6", "#A78BFA", "#C4B5FD", "#DDD6FE"],
            fonts=["Playfair Display", "Crimson Text", "Lora"],
            logo_urls=["https://placeholder.com/logo-royal.png"]
        )
    ]
    
    # Insert brand kits
    for brand_kit in brand_kits:
        await db.brand_kits.insert_one(brand_kit.dict())
    
    print(f"✅ Seeded {len(brand_kits)} brand kits")
    
    # Seed Export History
    exports = [
        Export(
            id="export_001",
            user_id="user_001",
            project_id="project_001",
            format=ExportFormat.MP4,
            resolution=ExportResolution.FULL_HD,
            aspect_ratio=AspectRatio.WIDESCREEN,
            fps=30,
            transparent_background=False,
            status=ExportStatus.DONE,
            progress=100,
            download_url="/downloads/export_001.mp4",
            file_size=4500000,
            actual_duration=45,
            completed_at=datetime.utcnow()
        ),
        Export(
            id="export_002",
            user_id="user_001",
            project_id="project_002",
            format=ExportFormat.WEBM_ALPHA,
            resolution=ExportResolution.FOUR_K,
            aspect_ratio=AspectRatio.WIDESCREEN,
            fps=30,
            transparent_background=True,
            status=ExportStatus.DONE,
            progress=100,
            download_url="/downloads/export_002.webm",
            file_size=12800000,
            actual_duration=120,
            completed_at=datetime.utcnow()
        ),
        Export(
            id="export_003",
            user_id="user_002",
            project_id="project_003",
            format=ExportFormat.GIF,
            resolution=ExportResolution.HD,
            aspect_ratio=AspectRatio.SQUARE,
            fps=24,
            transparent_background=False,
            status=ExportStatus.RENDERING,
            progress=65,
            estimated_duration=30
        ),
        Export(
            id="export_004",
            user_id="user_001",
            project_id="project_001",
            format=ExportFormat.LOTTIE_JSON,
            resolution=ExportResolution.CUSTOM,
            custom_width=1080,
            custom_height=1080,
            aspect_ratio=AspectRatio.SQUARE,
            fps=30,
            transparent_background=True,
            status=ExportStatus.FAILED,
            progress=0,
            error_message="Invalid Lottie animation structure"
        )
    ]
    
    # Insert exports
    for export in exports:
        await db.exports.insert_one(export.dict())
    
    print(f"✅ Seeded {len(exports)} exports")
    
    client.close()
    print("🎉 Comprehensive database seeding completed successfully!")
    print("\n📊 Summary:")
    print(f"  • {len(templates)} Templates with detailed schemas")
    print(f"  • {len(template_assets)} Template Assets")  
    print(f"  • {len(projects)} User Projects")
    print(f"  • {len(brand_kits)} Brand Kits")
    print(f"  • {len(exports)} Export Records")

if __name__ == "__main__":
    asyncio.run(seed_database())