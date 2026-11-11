# Phase 3 — Live Competitor Discovery & Research

## Goal
Add live competitor discovery, manual competitor research, structured comparisons and source-linked evidence to PitchIntel AI.

## Features
- Automatic competitor discovery from live web search.
- Manual competitor list and combined automatic + manual mode.
- Individual search queries per competitor for products, features, pricing and positioning.
- OpenAI or Gemini extracts structured findings from retrieved search snippets.
- Report includes market overview, competitive themes, pitch opportunities, competitor findings and source links.
- Citation IDs are allow-listed against the exact source set returned by search. Unknown citation IDs are discarded.
- Missing pricing/features are reported as unavailable rather than invented.

## Architecture
React UI -> FastAPI /api/v1/competitive-research -> Tavily Search API -> OpenAI/Gemini structured extraction -> source validation -> JSON response.

## Configuration
Add to backend/.env:
TAVILY_API_KEY=your_tavily_api_key

Get a key from https://tavily.com/. Keep it on the backend only. Existing OpenAI and Gemini keys are used for extraction.

## API
POST /api/v1/competitive-research

JSON body:
{
  "company_name": "Acme",
  "industry": "CRM software",
  "competitors": ["Salesforce", "HubSpot"],
  "research_mode": "both",
  "provider": "openai"
}

research_mode is automatic, manual or both. Automatic discovers competitor names from search results. Manual researches only supplied names. Both combines discovered and supplied names.

## Run
From backend/: pip install -r requirements.txt
uvicorn app.main:app --reload
pytest

## Evidence and limitations
- Every citation URL originates from a Tavily result. The API validates citation IDs against the retrieved source set and drops unknown IDs.
- This is source-link validation, not a guarantee that a page semantically proves every generated statement. A human should open and verify important claims.
- Search snippets can be incomplete, stale or promotional. Pricing may be unavailable or region-specific.
- Tavily is a required external service for live research. Provider calls can incur usage charges.
- Authentication, quotas, persistent research history, scheduled refresh, exportable reports and production observability remain future work.
