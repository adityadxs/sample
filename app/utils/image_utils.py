"""Image processing utilities for loading, validation, and cropping."""
import io
import os
import uuid
from typing import List, Tuple
from PIL import Image
from fastapi import HTTPException, UploadFile, status
from app.config import settings
from app.utils.logging import logger


def validate_upload_image(file: UploadFile) -> None:
    """Validate image extension and content type."""
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}",
        )


def read_image_from_bytes(data: bytes) -> Image.Image:
    """Convert raw image bytes into RGB PIL Image."""
    try:
        image = Image.open(io.BytesIO(data))
        return image.convert("RGB")
    except Exception as e:
        logger.error(f"Failed to decode image bytes: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file could not be decoded as a valid image.",
        )


def crop_bottle_bounding_box(
    image: Image.Image,
    bbox: List[float],
) -> Image.Image:
    """Safely crop bottle area from an image given [x1, y1, x2, y2]."""
    width, height = image.size
    x1, y1, x2, y2 = bbox

    # Clamp coordinates to image boundaries
    x1_clamped = max(0, min(int(x1), width - 1))
    y1_clamped = max(0, min(int(y1), height - 1))
    x2_clamped = max(x1_clamped + 1, min(int(x2), width))
    y2_clamped = max(y1_clamped + 1, min(int(y2), height))

    return image.crop((x1_clamped, y1_clamped, x2_clamped, y2_clamped))


def save_image_to_disk(
    image: Image.Image,
    directory: str,
    prefix: str = "img",
) -> Tuple[str, str]:
    """Save PIL Image to disk and return (unique_id, absolute_file_path)."""
    os.makedirs(directory, exist_ok=True)
    unique_id = str(uuid.uuid4())
    filename = f"{prefix}_{unique_id}.jpg"
    full_path = os.path.join(directory, filename)
    image.save(full_path, "JPEG", quality=95)
    return unique_id, full_path
