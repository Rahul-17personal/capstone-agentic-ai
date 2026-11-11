# Phase 4 — Report Export

## Deliverables
Generate a report from the existing PitchIntel analysis without rerunning AI:
- PDF: formatted report with score table, analysis, competitive intelligence and clickable source links.
- DOCX: editable Word report with headings, score table, recommendations and source URLs.
- PPTX: presentation with summary, score, metrics, findings, opportunities and source slides.

## API
POST /api/v1/reports/pdf
POST /api/v1/reports/docx
POST /api/v1/reports/pptx

JSON request:
{
  "company_name": "Acme",
  "source_filename": "sales-pitch.pdf",
  "analysis": { "executive_summary": "...", "overall_score": 78 },
  "competitive_research": { "market_overview": "...", "findings": [], "sources": [] },
  "workflow": { "completed_agents": ["strategist", "critic", "sales_coach", "report_synthesizer"] }
}

The analysis object is required and should be the exact result returned by /api/v1/agent-workflow. competitive_research is optional; pass the Phase 3 result when available. The API responds with a file attachment. The frontend downloads each format through a Blob URL.

## Run and test
From backend:
pip install -r requirements.txt
pytest

## Notes
- Exports use reportlab, python-docx and python-pptx, already listed in backend requirements.
- Generation is synchronous and in-memory; files are not persisted on the server.
- Very long source lists or pitch text may produce large presentations. Authentication, quotas and background jobs are production hardening tasks.
