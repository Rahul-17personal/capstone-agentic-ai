# PitchIntel AI

Sales Pitch Review & Competitive Intelligence web application.

## Current implementation
- **Phase 1:** React + Vite dashboard, FastAPI API, PDF/DOCX/PPTX text extraction, OpenAI and Gemini provider support.
- **Phase 2:** LangGraph multi-agent workflow with a Sales Strategist, Pitch Critic, Sales Coach and Report Synthesizer.
- **Phase 3:** Live competitor discovery and research (automatic/manual/both), source-linked findings, pricing/features observations and pitch opportunities using Tavily plus OpenAI/Gemini.
- **Not yet implemented:** exportable reports, database persistence and AWS deployment.

## Stack
- Frontend: React + Vite
- Backend: Python 3.11+ + FastAPI
- Orchestration: LangGraph
- Models: OpenAI Responses API and Google Gemini
- Documents: PyMuPDF, python-docx, python-pptx
- Validation: Pydantic

## Requirements
Python 3.11+, Node.js 20+, npm, and at least one provider API key.

## Backend setup
```bash
cd backend
python -m venv .venv
# PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env and add your provider key(s)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Health: http://127.0.0.1:8000/api/v1/health  
Swagger: http://127.0.0.1:8000/docs

## Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## API endpoints
- `GET /api/v1/health` — health check
- `POST /api/v1/analyze` — Phase 1 single-pass analysis
- `POST /api/v1/agent-workflow` — Phase 2 LangGraph workflow (multipart: file, provider=openai|gemini, competitors optional comma-separated names)
- `POST /api/v1/competitive-research` — Phase 3 live competitor research (JSON: company_name, industry, competitors, research_mode, provider)

## Phase 2 workflow
1. Strategist: positioning, value proposition, audience and proof points.
2. Critic: messaging scores, strengths, weaknesses, missing information and risks.
3. Sales Coach: recommendations and rewritten pitch.
4. Report Synthesizer: consolidates agent results into the Phase 1 report schema.

The current graph is sequential; every agent uses the selected provider. User-supplied competitor names are context only. No live competitive research is performed in Phase 2.

## Phase 3 competitive research

Set `TAVILY_API_KEY` in `backend/.env` to enable live web search. Use `research_mode=automatic` to discover competitors, `manual` to research only supplied names, or `both` to combine them. Every displayed citation URL is selected from actual search results. Citation-ID validation is deterministic; semantic claim verification still requires a human to inspect important sources. See `docs/PHASE-3-COMPETITIVE-INTELLIGENCE.md`.

## Tests
From `backend/` run:
```bash
pytest
```
The workflow test stubs the model adapter and does not require live API keys. Live model calls can incur provider usage charges.

## Security and limitations
Never commit `.env` files or expose provider keys in frontend code. Uploaded content is sent to the selected AI provider. Only upload documents you are authorised to share. Temporary uploads are deleted after processing. Scanned/image-only files are not OCR-processed yet. Before production, add authentication, rate limits, malware/content validation, secure storage, retries/timeouts, audit logging and observability.

## Roadmap
1. Phase 1 — application foundation and dual-provider document analysis.
2. Phase 2 — LangGraph multi-agent workflow.
3. Phase 3 — live competitor discovery/research with source URLs and evidence validation (implemented).
4. Phase 4 — PDF, DOCX and PPTX report generation.
5. Phase 5 — PostgreSQL, S3, authentication and background jobs.
6. Phase 6 — Docker, AWS deployment, CI/CD and monitoring.
