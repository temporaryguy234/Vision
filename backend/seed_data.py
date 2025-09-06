import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

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
    await db.projects.delete_many({})
    await db.brand_kits.delete_many({})
    await db.exports.delete_many({})
    
    print("🧹 Cleared existing data")
    
    # Seed Templates
    templates = [
        {
            "id": "1",
            "title": "Modern Social Intro",
            "description": "Eye-catching social media intro with smooth transitions",
            "category": "Intros & Outros",
            "preview": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=400&h=300&fit=crop",
            "tags": ["Instagram", "TikTok", "Modern", "Trendy"],
            "duration": "5s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 1250,
            "rating": 4.8,
            "template_data": {
                "elements": [
                    {"id": "title", "type": "text", "content": "Your Brand", "x": 50, "y": 30},
                    {"id": "subtitle", "type": "text", "content": "Professional Content", "x": 50, "y": 60}
                ]
            }
        },
        {
            "id": "2",
            "title": "Data Chart Animation",
            "description": "Professional data visualization with animated charts",
            "category": "Charts & Maps",
            "preview": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
            "tags": ["Charts", "Analytics", "Business", "Professional"],
            "duration": "8s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 890,
            "rating": 4.6,
            "template_data": {
                "elements": [
                    {"id": "chart", "type": "chart", "chartType": "bar", "data": [10, 20, 30, 40]},
                    {"id": "title", "type": "text", "content": "Sales Report", "x": 50, "y": 10}
                ]
            }
        },
        {
            "id": "3",
            "title": "Logo Reveal",
            "description": "Elegant logo animation with particle effects",
            "category": "Animated Icons",
            "preview": "https://images.unsplash.com/photo-1558655146-9f40138edfeb?w=400&h=300&fit=crop",
            "tags": ["Logo", "Branding", "Corporate", "Clean"],
            "duration": "3s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 2100,
            "rating": 4.9,
            "template_data": {
                "elements": [
                    {"id": "logo", "type": "image", "src": "logo.png", "x": 50, "y": 50},
                    {"id": "particles", "type": "effect", "effectType": "particles"}
                ]
            }
        },
        {
            "id": "4",
            "title": "Inspirational Quote",
            "description": "Beautiful typography animation for motivational content",
            "category": "Titles & Quotes",
            "preview": "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=400&h=300&fit=crop",
            "tags": ["Typography", "Motivational", "Social", "Elegant"],
            "duration": "6s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 1680,
            "rating": 4.7,
            "template_data": {
                "elements": [
                    {"id": "quote", "type": "text", "content": "\"Dream Big, Work Hard\"", "x": 50, "y": 40},
                    {"id": "author", "type": "text", "content": "- Motivational", "x": 50, "y": 60}
                ]
            }
        },
        {
            "id": "5",
            "title": "Product Showcase",
            "description": "Dynamic product presentation with 3D effects",
            "category": "Ads & Promos",
            "preview": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400&h=300&fit=crop",
            "tags": ["Product", "Marketing", "E-commerce", "Sales"],
            "duration": "10s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 750,
            "rating": 4.5,
            "template_data": {
                "elements": [
                    {"id": "product", "type": "image", "src": "product.png", "x": 30, "y": 50},
                    {"id": "title", "type": "text", "content": "New Product", "x": 70, "y": 30},
                    {"id": "price", "type": "text", "content": "$99", "x": 70, "y": 70}
                ]
            }
        },
        {
            "id": "6",
            "title": "World Map Data",
            "description": "Interactive world map with data visualization",
            "category": "Charts & Maps",
            "preview": "https://images.unsplash.com/photo-1597149961283-62c2e52b98d6?w=400&h=300&fit=crop",
            "tags": ["Maps", "Global", "Data", "Infographic"],
            "duration": "7s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 920,
            "rating": 4.4,
            "template_data": {
                "elements": [
                    {"id": "map", "type": "map", "region": "world", "x": 50, "y": 50},
                    {"id": "title", "type": "text", "content": "Global Statistics", "x": 50, "y": 10}
                ]
            }
        },
        {
            "id": "7",
            "title": "Lower Third News",
            "description": "Professional news-style lower third graphics",
            "category": "Lower Thirds",
            "preview": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=300&fit=crop",
            "tags": ["News", "Professional", "Broadcast", "Clean"],
            "duration": "4s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 1350,
            "rating": 4.8,
            "template_data": {
                "elements": [
                    {"id": "name", "type": "text", "content": "John Doe", "x": 20, "y": 80},
                    {"id": "title", "type": "text", "content": "Senior Analyst", "x": 20, "y": 85}
                ]
            }
        },
        {
            "id": "8",
            "title": "Social Media Story",
            "description": "Vertical story template for Instagram and TikTok",
            "category": "Social Media Posts",
            "preview": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop",
            "tags": ["Stories", "Instagram", "Mobile", "Vertical"],
            "duration": "15s",
            "is_public": True,
            "creator_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "download_count": 3200,
            "rating": 4.9,
            "template_data": {
                "elements": [
                    {"id": "background", "type": "image", "src": "bg.jpg", "x": 50, "y": 50},
                    {"id": "text", "type": "text", "content": "Your Story", "x": 50, "y": 20}
                ]
            }
        }
    ]
    
    await db.templates.insert_many(templates)
    print(f"✅ Seeded {len(templates)} templates")
    
    # Seed Sample Projects
    projects = [
        {
            "id": "proj1",
            "title": "Summer Campaign Video",
            "template_id": "1",
            "template_title": "Modern Social Intro",
            "thumbnail": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=300&h=200&fit=crop",
            "status": "Draft",
            "duration": "15s",
            "user_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "project_data": {
                "elements": [
                    {"id": "title", "type": "text", "content": "Summer Sale 2024", "color": "#ff6b35"},
                    {"id": "subtitle", "type": "text", "content": "Up to 50% Off", "color": "#1a1a1a"}
                ]
            }
        },
        {
            "id": "proj2",
            "title": "Q4 Sales Report",
            "template_id": "2",
            "template_title": "Data Chart Animation",
            "thumbnail": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=200&fit=crop",
            "status": "Completed",
            "duration": "30s",
            "user_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "project_data": {
                "elements": [
                    {"id": "chart", "type": "chart", "data": [45, 67, 89, 102], "color": "#3b82f6"},
                    {"id": "title", "type": "text", "content": "Q4 Performance", "color": "#1f2937"}
                ]
            }
        }
    ]
    
    await db.projects.insert_many(projects)
    print(f"✅ Seeded {len(projects)} projects")
    
    # Seed Brand Kits
    brand_kits = [
        {
            "id": "kit1",
            "name": "Corporate Blue",
            "description": "Professional and trustworthy brand colors",
            "colors": ["#1E40AF", "#3B82F6", "#60A5FA", "#93C5FD", "#DBEAFE"],
            "fonts": ["Inter", "Roboto"],
            "user_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": "kit2",
            "name": "Sunset Gradient",
            "description": "Warm and energetic brand palette",
            "colors": ["#EA580C", "#F97316", "#FB923C", "#FDBA74", "#FED7AA"],
            "fonts": ["Poppins", "Open Sans"],
            "user_id": "user1",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await db.brand_kits.insert_many(brand_kits)
    print(f"✅ Seeded {len(brand_kits)} brand kits")
    
    # Seed Export History
    exports = [
        {
            "id": "exp1",
            "project_id": "proj1",
            "project_name": "Summer Campaign Video",
            "format": "MP4",
            "resolution": "1080p",
            "size": "45.2 MB",
            "duration": "15s",
            "status": "Completed",
            "user_id": "user1",
            "exported_at": datetime.utcnow(),
            "download_url": "https://example.com/download/exp1.mp4"
        },
        {
            "id": "exp2",
            "project_id": "proj2",
            "project_name": "Q4 Sales Report",
            "format": "WebM",
            "resolution": "4K",
            "size": "128.7 MB",
            "duration": "30s",
            "status": "Completed",
            "user_id": "user1",
            "exported_at": datetime.utcnow(),
            "download_url": "https://example.com/download/exp2.webm"
        }
    ]
    
    await db.exports.insert_many(exports)
    print(f"✅ Seeded {len(exports)} exports")
    
    await client.close()
    print("🎉 Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_database())