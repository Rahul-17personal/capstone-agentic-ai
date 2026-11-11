# PitchIntel AI

Sales Pitch Review & Competitive Intelligence web application.

Phase 1 provides a React dashboard and FastAPI backend for PDF, DOCX and PPTX text extraction, plus AI pitch analysis using OpenAI Responses API or Google Gemini. User-entered competitor names are context only; live competitor research is planned for Phase 3.

## Stack
- React + Vite
- Python + FastAPI
- OpenAI Python SDK and Google GenAI SDK
- PyMuPDF, python-docx, python-pptx
- Pydantic

## Requirements
Python 3.11+, Node.js 20+, npm, and at least one AI provider API key.

## Backend
```bash
cd backend
python -m venv .venv
# PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env and add your API key
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
API health: http://127.0.0.1:8000/api/v1/health ; Swagger: http://127.0.0.1:8000/docs

## Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## API
`GET /api/v1/health`; `POST /api/v1/analyze` (multipart: file, provider=openai|gemini, competitors optional comma-separated list).

## Security
Never commit `.env` files or expose API keys to the browser. Uploaded content is sent to the selected AI provider. Only upload files you are authorised to share. This is a development foundation: production needs content-signature validation, malware scanning, auth, rate limiting, private storage and redacted logs. Scanned/image-only documents are not parsed yet.

## Roadmap
1. Phase 1 foundation and dual-provider document analysis.
2. Phase 2 LangGraph multi-agent workflow.
3. Phase 3 live competitor discovery/research with sources and evidence verification.
4. Phase 4 PDF, DOCX and PPTX report generation.
5. Phase 5 PostgreSQL, S3, authentication and background jobs.
6. Phase 6 Docker, AWS deployment, CI/CD and monitoring.
