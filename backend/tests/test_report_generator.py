from app.services.report_generator import build_docx, build_pdf, build_pptx

SAMPLE = {
    "company_name": "Acme",
    "analysis": {
        "executive_summary": "Clear value proposition, but evidence is limited.",
        "overall_score": 78,
        "strengths": ["Clear target audience"],
        "weaknesses": ["Missing quantified proof"],
        "messaging_quality": 80,
        "value_proposition": 75,
        "target_audience_clarity": 82,
        "call_to_action": 74,
        "missing_information": ["Customer outcomes"],
        "recommendations": ["Add measurable proof"],
        "improved_pitch": "We help teams improve their workflow.",
        "competitor_context": "Competitor context is supplied separately.",
    },
    "competitive_research": {
        "market_overview": "A competitive market.",
        "competitive_themes": ["Automation"],
        "pitch_opportunities": ["Show measurable ROI"],
        "findings": [{
            "name": "Beta",
            "summary": "A competing platform.",
            "positioning": "Mid-market",
            "products_and_features": ["Workflow automation"],
            "pricing_observations": ["Public pricing not found"],
            "differentiators": ["Integrations"],
            "caveats": [],
            "source_ids": ["S1"],
        }],
        "sources": [{"source_id": "S1", "title": "Example", "url": "https://example.com"}],
    },
}


def test_build_pdf_returns_pdf_bytes():
    assert build_pdf(SAMPLE).startswith(b"%PDF")


def test_build_docx_returns_zip_bytes():
    assert build_docx(SAMPLE).startswith(b"PK")


def test_build_pptx_returns_zip_bytes():
    assert build_pptx(SAMPLE).startswith(b"PK")
