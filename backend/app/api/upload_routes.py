from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.config import settings
from app.dependencies import get_current_user
from app.models import User
from app.services.object_storage import upload_bytes

router = APIRouter(prefix="/uploads")
ALLOWED = {".pdf", ".docx", ".pptx"}


@router.post("/pitch")
async def upload_pitch(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    filename = Path(file.filename or "pitch").name
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX and PPTX are supported")
    content = await file.read(settings.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Upload exceeds configured size limit")
    key = f"users/{user.id}/pitches/{uuid4().hex}{extension}"
    try:
        upload_bytes(content, key, file.content_type or "application/octet-stream")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="S3 upload failed; check backend AWS permissions") from exc
    return {"object_key": key, "filename": filename, "size_bytes": len(content)}
