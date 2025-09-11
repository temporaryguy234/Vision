# 🎬 MotionEdit API v2.0.0 - Comprehensive Documentation

## Overview

MotionEdit is a comprehensive motion graphics template platform with advanced data modeling, file storage, and editable parameter validation. This system allows users to import high-quality motion graphics templates, duplicate them into projects, edit with natural language commands, and export in multiple formats.

## 🗄️ Database Schema

### Templates Collection
Stores template metadata and editable parameter schemas.

**Fields:**
- `id`: Unique template identifier
- `title`: Human-readable template name
- `slug`: URL-friendly version of title
- `category`: Template category (enum)
- `tags`: Array of searchable tags
- `preview_image_url`: Template preview image
- `supported_aspect_ratios`: Supported output ratios
- `editable_parameters_schema`: Comprehensive parameters definition
- `creator_id`: Template creator identifier
- `version`: Template version (semantic versioning)
- `is_public`: Public visibility flag
- `download_count`: Usage statistics
- `rating`: User rating (0-5)
- `created_at`, `updated_at`: Timestamps

### Template Assets Collection
Stores actual template files (Lottie, videos, images).

**Fields:**
- `id`: Unique asset identifier
- `template_id`: Parent template reference
- `asset_type`: File type (Lottie JSON, MP4, WebM, GIF, PNG, SVG)
- `file_url`: Public asset URL
- `width`, `height`: Asset dimensions
- `duration`: Length in seconds (for animated assets)
- `frame_rate`: FPS for video assets
- `file_size`: File size in bytes
- `created_at`, `updated_at`: Timestamps

### Projects Collection
User projects created from templates.

**Fields:**
- `id`: Unique project identifier
- `user_id`: Project owner
- `template_id`: Source template reference
- `title`: Project name
- `status`: Project status (Draft, In Progress, Completed)
- `current_editor_state`: User's edits and modifications
- `thumbnail_url`: Generated project thumbnail
- `duration`: Project duration in seconds
- `created_at`, `updated_at`: Timestamps

### Brand Kits Collection
User-saved brand elements.

**Fields:**
- `id`: Unique brand kit identifier
- `user_id`: Brand kit owner
- `name`: Brand kit name
- `description`: Brand kit description
- `colors`: Array of hex colors
- `fonts`: Array of font family names
- `logo_urls`: Array of logo image URLs
- `created_at`, `updated_at`: Timestamps

### Exports Collection
Export job tracking and history.

**Fields:**
- `id`: Unique export identifier
- `user_id`: Export owner
- `project_id`: Source project reference
- `format`: Export format (MP4, GIF, WebM, Lottie)
- `resolution`: Output resolution (4K, 1080p, 720p, custom)
- `aspect_ratio`: Output aspect ratio
- `custom_width`, `custom_height`: Custom dimensions
- `fps`: Frame rate
- `transparent_background`: Transparency flag
- `status`: Export status (queued, rendering, done, failed)
- `progress`: Completion percentage (0-100)
- `download_url`: Final file URL
- `file_size`: Output file size
- `error_message`: Error details if failed
- `estimated_duration`, `actual_duration`: Render time tracking
- `created_at`, `updated_at`, `completed_at`: Timestamps

## 🎨 Editable Parameters Schema

Each template defines exactly what can be edited and with what constraints.

### Canvas Parameters
- **Width/Height**: 100-4000 pixels
- **Background Color**: Hex color or "transparent"
- **Global Playback Speed**: 0.5×-2.0× multiplier

### Element Types & Parameters

#### Text Elements
- **Content**: Max 500 characters
- **Font Family**: Predefined font list
- **Font Size**: 12-180 pixels
- **Color**: Hex color format
- **Alignment**: left/center/right
- **Opacity**: 0.0-1.0
- **Position**: X/Y as percentage (0-100)
- **Scale**: 0.1-5.0 multiplier
- **Rotation**: -360° to 360°
- **Entrance Animation**: Optional animation settings

#### Image/Logo Elements
- **Source URL**: Replaceable image
- **Fit**: cover/contain
- **Opacity**: 0.0-1.0
- **Position/Scale/Rotation**: Same as text
- **Entrance Animation**: Optional

#### Shape Elements
- **Fill Color**: Hex color
- **Stroke Color**: Optional hex color
- **Stroke Width**: 0-20 pixels
- **Corner Radius**: 0-100 pixels
- **Opacity**: 0.0-1.0
- **Position/Scale/Rotation**: Same as text
- **Entrance Animation**: Optional

#### Chart Elements
- **Chart Type**: line/bar/pie
- **Series Colors**: Array of hex colors
- **Show Labels**: Boolean flag
- **Line Width**: 0-20 pixels (line charts)
- **Bar Width**: 1-40 pixels (bar charts)
- **Data Placeholder**: Sample data array
- **Position/Scale**: X/Y position and scale
- **Entrance Animation**: Optional

#### Map Elements
- **Focus Region**: Geographic focus (world, country code, region)
- **Land Color**: Hex color for land masses
- **Border Color**: Hex color for borders
- **Border Width**: 0-12 pixels
- **Show Labels**: Boolean flag
- **Position/Scale**: X/Y position and scale
- **Entrance Animation**: Optional

### Entrance Animations
- **Types**: fly-in (left/right/top/bottom), fade-in, scale-in, bounce-in
- **Delay**: 0-5 seconds
- **Duration**: 0.5-5 seconds
- **Easing**: ease, ease-in, ease-out, linear

## 🔌 API Endpoints

### Templates API

#### GET /api/templates
Get templates with filtering and sorting.

**Query Parameters:**
- `category`: Filter by template category
- `search`: Case-insensitive search on template titles and tags
- `tags`: Comma-separated tag filter
- `creator_id`: Filter by creator
- `is_public`: Public/private filter
- `limit`: Results limit (max 100)
- `skip`: Pagination offset
- `sort_by`: Sort field (created_at, title, download_count, rating)
- `sort_order`: asc/desc

**Response:** Array of Template objects

#### POST /api/templates
Create new template (admin only).

**Body:** TemplateCreate object
**Response:** Created Template object

#### GET /api/templates/{template_id}
Get specific template by ID.

**Response:** Template object

#### GET /api/templates/slug/{slug}
Get template by URL-friendly slug.

**Response:** Template object

#### PUT /api/templates/{template_id}
Update template (admin only).

**Body:** TemplateUpdate object
**Response:** Updated Template object

#### DELETE /api/templates/{template_id}
Delete template and all assets.

**Response:** Success message

### Template Assets API

#### GET /api/templates/{template_id}/assets
Get all assets for a template.

**Response:** Array of TemplateAsset objects

#### POST /api/templates/{template_id}/assets
Create asset record manually.

**Body:** TemplateAssetCreate object
**Response:** Created TemplateAsset

#### POST /api/templates/{template_id}/upload-asset
Upload file asset for template.

**Body:** Multipart form with file
**Response:** Created TemplateAsset with metadata

#### DELETE /api/templates/{template_id}/assets/{asset_id}
Delete asset file and record.

**Response:** Success message

### Projects API

#### GET /api/projects
Get user projects.

**Query Parameters:**
- `user_id`: Required - project owner
- `status`: Filter by project status
- `template_id`: Filter by source template
- `limit`, `skip`: Pagination

**Response:** Array of Project objects

#### POST /api/projects
Create project from template.

**Body:** ProjectCreate object
**Response:** Created Project with initialized editor state

#### GET /api/projects/{project_id}
Get specific project.

**Response:** Project object

#### PUT /api/projects/{project_id}
Update project data.

**Body:** ProjectUpdate object
**Response:** Updated Project

#### DELETE /api/projects/{project_id}
Delete project.

**Response:** Success message

### Brand Kits API

#### GET /api/brand-kits
Get user brand kits.

**Query Parameters:**
- `user_id`: Required - brand kit owner
- `limit`, `skip`: Pagination

**Response:** Array of BrandKit objects

#### POST /api/brand-kits
Create brand kit.

**Body:** BrandKitCreate object
**Response:** Created BrandKit

#### PUT /api/brand-kits/{kit_id}
Update brand kit.

**Body:** BrandKitUpdate object
**Response:** Updated BrandKit

#### DELETE /api/brand-kits/{kit_id}
Delete brand kit.

**Response:** Success message

### Exports API

#### GET /api/exports
Get user exports.

**Query Parameters:**
- `user_id`: Required - export owner
- `project_id`: Filter by source project
- `status`: Filter by export status
- `limit`, `skip`: Pagination

**Response:** Array of Export objects

#### POST /api/exports
Create export job.

**Body:** ExportCreate object
**Response:** Created Export (queued for processing)

#### GET /api/exports/{export_id}
Get specific export.

**Response:** Export object

#### PUT /api/exports/{export_id}/status
Update export status (internal use).

**Query Parameters:**
- `status`: New export status
- `progress`: Completion percentage
- `download_url`: Final file URL
- `error_message`: Error details

**Response:** Success message

### Statistics API

#### GET /api/stats
Get platform statistics.

**Response:**
```json
{
  "templates": "5+",
  "projects": "3+", 
  "exports": "4+",
  "active_creators": "10K+",
  "time_saved": "95%",
  "avg_edit_time": "2 Min"
}
```

## 📁 File Storage System

### Supported File Types
- **Lottie JSON**: Vector animations (.json)
- **MP4**: Standard video format
- **WebM with Alpha**: Web video with transparency
- **GIF**: Animated images
- **PNG**: Static images
- **SVG**: Vector graphics

### File Organization
```
/app/uploads/
├── lottie/
│   └── {template_id}/
├── videos/
│   ├── mp4/
│   └── webm/
├── images/
│   ├── png/
│   ├── gif/
│   └── svg/
└── thumbnails/
```

### Upload Flow
1. **File Validation**: Check type and format
2. **Metadata Extraction**: Get dimensions, duration, frame rate
3. **Unique Naming**: Generate collision-free filename
4. **Storage**: Save to appropriate directory
5. **Database Record**: Create TemplateAsset entry
6. **Thumbnail Generation**: Auto-generate preview (videos/images)

### File Validation
- **Lottie JSON**: Validate required fields (v, fr, ip, op, w, h, layers)
- **Video Files**: Extract metadata using ffprobe
- **Images**: Get dimensions using Pillow
- **Size Limits**: Configurable per asset type
- **Format Validation**: Strict MIME type checking

## 🔐 Parameter Validation

### Validation Rules
All editable parameters are validated against strict constraints:

- **Numeric Ranges**: Font sizes (12-180px), positions (0-100%), etc.
- **Color Formats**: Hex colors (#RRGGBB) or special values
- **Enum Values**: Predefined choices for alignments, chart types, etc.
- **String Lengths**: Character limits for text content
- **Array Validation**: Color arrays, data arrays with type checking
- **Animation Constraints**: Timing limits, easing types

### Error Handling
Invalid parameters return detailed error messages:
```json
{
  "message": "Invalid editable parameters",
  "errors": {
    "elements[0].font_size": "Font size must be between 12 and 180 pixels",
    "elements[1].stroke_width": "Stroke width must be between 0 and 20 pixels"
  }
}
```

## 🚀 Example Usage

### Create Template with Schema
```python
template_data = {
    "title": "Social Media Post",
    "category": "Social Media Posts",
    "tags": ["Instagram", "Square", "Modern"],
    "preview_image_url": "https://example.com/preview.jpg",
    "supported_aspect_ratios": ["1:1"],
    "editable_parameters_schema": {
        "canvas": {
            "width": 1080,
            "height": 1080,
            "background_color": "#FFFFFF",
            "global_playback_speed": 1.0
        },
        "elements": [
            {
                "id": "main_text",
                "type": "text",
                "name": "Main Text",
                "parameters": {
                    "content": "Your Message Here",
                    "font_family": "Inter",
                    "font_size": 36,
                    "color": "#000000",
                    "alignment": "center",
                    "x": 50.0,
                    "y": 50.0
                }
            }
        ]
    },
    "creator_id": "admin_001"
}
```

### Upload Template Asset
```bash
curl -X POST "http://localhost:8001/api/templates/template_001/upload-asset" \
  -F "file=@animation.json"
```

### Create Project from Template
```python
project_data = {
    "template_id": "template_001",
    "title": "My Social Post",
    "user_id": "user_123"
}
```

### Export Project
```python
export_data = {
    "project_id": "project_001",
    "user_id": "user_123",
    "format": "MP4",
    "resolution": "1080p",
    "aspect_ratio": "1:1",
    "fps": 30,
    "transparent_background": false
}
```

## 🔧 Development Setup

### Dependencies
- FastAPI 0.110.1
- Motor 3.3.1 (MongoDB async driver)
- Pydantic 2.11+ (data validation)
- Pillow 10.0+ (image processing)
- aiofiles 24.1+ (async file operations)

### Environment Variables
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=motionedit
CORS_ORIGINS=http://localhost:3000
```

### Run Server
```bash
cd /app/backend
python server.py
```

### Seed Database
```bash
python seed_new_data.py
```

## 📈 Performance Considerations

### Database Indexing
Recommended indexes:
- `templates.slug` (unique)
- `templates.category`
- `templates.is_public`
- `projects.user_id`
- `projects.template_id`
- `exports.user_id`
- `exports.status`

### File Storage Optimization
- CDN integration for public asset URLs
- Automatic thumbnail generation
- File compression for large assets
- Cleanup of orphaned files

### API Rate Limiting
- Template uploads: 10 per minute per user
- Export jobs: 5 per minute per user
- General API: 1000 per minute per user

This comprehensive system provides a solid foundation for a production-ready motion graphics template platform with robust data modeling, file handling, and parameter validation.