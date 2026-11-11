from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import settings
from app.dependencies import get_current_user
from app.models import User
from app.services.competitor_research import run_competitor_research

router = APIRouter()


class CompetitiveResearchRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=160)
    industry: str = Field(default="", max_length=160)
    competitors: list[str] = Field(default_factory=list, max_length=20)
    research_mode: str = "both"
    provider: str = settings.DEFAULT_AI_PROVIDER


@router.post("/competitive-research")
def competitive_research(request: CompetitiveResearchRequest, user: User = Depends(get_current_user)):
    """Discover and compare competitors using live web search and source-linked findings."""
    if request.provider.lower() not in {"openai", "gemini"}:
        raise HTTPException(status_code=400, detail="Provider must be openai or gemini")
    try:
        result = run_competitor_research(
            company_name=request.company_name,
            industry=request.industry,
            competitors=request.competitors,
            research_mode=request.research_mode,
            provider=request.provider.lower(),
        )
        return {"status": "success", "provider": request.provider.lower(), "research": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Competitive research failed. Check Tavily/provider configuration and backend logs.",
        ) from exc
