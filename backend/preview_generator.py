from pathlib import Path
from PIL import Image, ImageDraw

def generate_preview(source_path: Path, preview_path: Path) -> None:
    """Generate a simple preview image for an uploaded template.

    This placeholder implementation creates a blank image so that the
    API returns a valid preview URL even when real rendering is unavailable.
    """
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (400, 300), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Preview", fill="black")
    img.save(preview_path)
