from __future__ import annotations

import os
import uuid

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile

from app.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-msvideo"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


@router.post("")
async def upload_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: images and videos.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Max 500 MB.")

    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    unique_name = f"{uuid.uuid4().hex}{ext}"

    upload_dir = os.path.join(settings.STORAGE_LOCAL_PATH, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {
        "filename": unique_name,
        "original_name": file.filename,
        "file_path": file_path,
        "file_size": len(content),
        "content_type": file.content_type,
    }
