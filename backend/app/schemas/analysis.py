from pydantic import BaseModel, Field


class PitchAnalysis(BaseModel):
    executive_summary: str
    overall_score: int = Field(ge=0, le=100)
    strengths: list[str]
    weaknesses: list[str]
    messaging_quality: int = Field(ge=0, le=100)
    value_proposition: int = Field(ge=0, le=100)
    target_audience_clarity: int = Field(ge=0, le=100)
    call_to_action: int = Field(ge=0, le=100)
    missing_information: list[str]
    recommendations: list[str]
    improved_pitch: str
    competitor_context: str
