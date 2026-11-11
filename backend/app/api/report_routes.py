from io import BytesIO
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.report_generator import build_docx, build_pdf, build_pptx

router = APIRouter()
BUILDERS = {
    "pdf": (build_pdf, "application/pdf"),
    "docx": ("docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    "pptx": ("pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
}


class ReportRequest(BaseModel):
    company_name: str = Field(default="Sales Pitch Review", max_length=160)
    analysis: dict
    competitive_research: dict | None = None
    workflow: dict | None = None
    source_filename: str | None = Field(default=None, max_length=240)


@router.post("/reports/{file_format}")
def export_report(file_format: str, request: ReportRequest):
    """Build a downloadable report using already-generated analysis data."""
    fmt = file_format.lower()
    if fmt not in BUILDERS:
        raise HTTPException(status_code=400, detail="Supported formats are pdf, docx and pptx")
    payload = request.model_dump()
    try:
        if fmt == "pdf":
            data = build_pdf(payload)
        elif fmt == "docx":
            data = build_docx(payload)
        else:
            data = build_pptx(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Report generation failed. Check backend logs.") from exc

    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", request.company_name).strip("-") or "PitchIntel"
    media_type = BUILDERS[fmt][1]
    return StreamingResponse(
        BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}-PitchIntel-Report.{fmt}"'},
    )
