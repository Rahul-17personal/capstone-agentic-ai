import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError

from app.config import settings
from app.services.ai_service import analyse_pitch
from app.services.document_parser import extract_text

router = APIRouter()
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx"}
MAX_TEXT_CHARS = 50_000


@router.get("/health")
def health_check():
    return {"status": "healthy", "application": settings.APP_NAME}


@router.post("/analyze")
async def analyze_sales_pitch(
    file: UploadFile = File(...),
    provider: str = Form(settings.DEFAULT_AI_PROVIDER),
    competitors: str = Form(""),
):
    filename = file.filename or "upload"
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX and PPTX are supported")
    if provider.lower() not in {"openai", "gemini"}:
        raise HTTPException(status_code=400, detail="Provider must be openai or gemini")

    content = await file.read(settings.MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB limit")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        pitch_text = extract_text(temp_path, extension)
        if not pitch_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No selectable text found. Scanned/image-only files are not supported yet.",
            )
        competitor_list = [item.strip()[:120] for item in competitors.split(",") if item.strip()][:20]
        result = analyse_pitch(pitch_text[:MAX_TEXT_CHARS], provider, competitor_list)
        return {
            "status": "success",
            "provider": provider.lower(),
            "filename": filename,
            "analysis": result.model_dump(),
        }
    except HTTPException:
        raise
    except (ValueError, ValidationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Analysis provider failed. Check server logs and API configuration.",
        ) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        await file.close()
