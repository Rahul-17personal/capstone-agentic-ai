from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import AnalysisRecord, User
from app.services.object_storage import create_download_url

router = APIRouter(prefix="/history")


class SaveAnalysisRequest(BaseModel):
    company_name: str = Field(default="Sales Pitch Review", max_length=160)
    source_filename: str | None = Field(default=None, max_length=240)
    analysis: dict
    competitive_research: dict | None = None
    source_s3_key: str | None = Field(default=None, max_length=1024)


def record_payload(record: AnalysisRecord) -> dict:
    return {
        "id": record.id,
        "company_name": record.company_name,
        "source_filename": record.source_filename,
        "overall_score": record.overall_score,
        "analysis": record.analysis,
        "competitive_research": record.competitive_research,
        "created_at": record.created_at.isoformat() if record.created_at else None,
        "has_source_file": bool(record.source_s3_key),
    }


@router.post("", status_code=201)
def save_analysis(request: SaveAnalysisRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    score = request.analysis.get("overall_score", 0)
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        score = 0
    record = AnalysisRecord(
        user_id=user.id, company_name=request.company_name,
        source_filename=request.source_filename, overall_score=score,
        analysis=request.analysis, competitive_research=request.competitive_research,
        source_s3_key=request.source_s3_key,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record_payload(record)


@router.get("")
def list_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records = db.scalars(
        select(AnalysisRecord).where(AnalysisRecord.user_id == user.id)
        .order_by(AnalysisRecord.created_at.desc()).limit(100)
    ).all()
    return {"items": [record_payload(record) for record in records]}


@router.get("/{record_id}")
def get_history(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.scalar(select(AnalysisRecord).where(
        AnalysisRecord.id == record_id, AnalysisRecord.user_id == user.id
    ))
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    result = record_payload(record)
    if record.source_s3_key:
        try:
            result["source_download_url"] = create_download_url(record.source_s3_key)
        except RuntimeError:
            result["source_download_url"] = None
    return result


@router.delete("/{record_id}", status_code=204)
def delete_history(record_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.scalar(select(AnalysisRecord).where(
        AnalysisRecord.id == record_id, AnalysisRecord.user_id == user.id
    ))
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    db.delete(record)
    db.commit()
