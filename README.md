# PitchIntel AI

Sales Pitch Review & Competitive Intelligence web application.

## Current implementation
- **Phase 1:** React + Vite dashboard, FastAPI API, PDF/DOCX/PPTX text extraction, OpenAI and Gemini provider support.
- **Phase 2:** LangGraph multi-agent workflow with a Sales Strategist, Pitch Critic, Sales Coach and Report Synthesizer.
- **Phase 3:** Live competitor discovery and research (automatic/manual/both), source-linked findings, pricing/features observations and pitch opportunities using Tavily plus OpenAI/Gemini.
- **Phase 4:** PDF, editable DOCX and PPTX report exports using the generated analysis and competitor research.
- **Phase 5:** JWT authentication, password hashing, PostgreSQL/SQLite persistence, per-user analysis history, private S3 upload and optional S3 report archival.
- **Phase 6:** Docker images, local Docker Compose, Nginx reverse proxy, GitHub Actions CI, GHCR image publishing and EC2 deployment workflow. AWS network/database/load-balancer resources are provisioned separately.

## Stack
- Frontend: React + Vite
- Backend: Python 3.11+ + FastAPI
- Orchestration: LangGraph
- Models: OpenAI Responses API and Google Gemini
- Persistence: SQLAlchemy with PostgreSQL (SQLite for local quick start)
- Authentication: JWT bearer tokens and Argon2 password hashing
- Object storage: private AWS S3 bucket using server-side encryption and short-lived presigned download URLs
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
- `POST /api/v1/reports/pdf` — generate PDF report
- `POST /api/v1/reports/docx` — generate editable Word report
- `POST /api/v1/reports/pptx` — generate PowerPoint presentation
- `POST /api/v1/auth/register` and `POST /api/v1/auth/login` — create account and authenticate
- `GET /api/v1/auth/me` — current account profile
- `GET|POST /api/v1/history` — list and save per-user analysis history
- `GET|DELETE /api/v1/history/{id}` — retrieve or delete an owned analysis
- `POST /api/v1/uploads/pitch` — upload a pitch file to private S3 (requires bucket configuration)

## Phase 2 workflow
1. Strategist: positioning, value proposition, audience and proof points.
2. Critic: messaging scores, strengths, weaknesses, missing information and risks.
3. Sales Coach: recommendations and rewritten pitch.
4. Report Synthesizer: consolidates agent results into the Phase 1 report schema.

The current graph is sequential; every agent uses the selected provider. User-supplied competitor names are context only. No live competitive research is performed in Phase 2.

## Phase 3 competitive research

Set `TAVILY_API_KEY` in `backend/.env` to enable live web search. Use `research_mode=automatic` to discover competitors, `manual` to research only supplied names, or `both` to combine them. Every displayed citation URL is selected from actual search results. Citation-ID validation is deterministic; semantic claim verification still requires a human to inspect important sources. See `docs/PHASE-3-COMPETITIVE-INTELLIGENCE.md`.

## Phase 4 report exports

After pitch analysis and competitor research, use the Download your report controls to export PDF, DOCX or PPTX. The frontend posts the existing report JSON to the matching `/api/v1/reports/{format}` endpoint; no extra AI analysis is run. Reports are generated in memory and returned as file attachments. See `docs/PHASE-4-REPORT-EXPORT.md`.

## Phase 6: Docker, AWS and CI/CD

See [`docs/PHASE-6-DOCKER-AWS-CICD.md`](docs/PHASE-6-DOCKER-AWS-CICD.md) for the full architecture and deployment guide.

Local container setup:

```bash
# Copy .env.compose.example to .env and backend/.env.example to backend/.env
# Add model API keys and a strong JWT_SECRET_KEY to backend/.env
docker compose up --build -d
docker compose ps
```

Open http://localhost:8080. CI runs backend tests, frontend build and Docker build checks. Pushes to `main` publish frontend/backend images to GHCR and deploy to a pre-provisioned EC2 host. Configure `EC2_HOST`, `EC2_USER`, `EC2_SSH_PRIVATE_KEY`, `EC2_APP_DIR`, `GHCR_USERNAME` and `GHCR_READ_TOKEN` as GitHub Actions secrets. Production uses RDS PostgreSQL and private S3; terminate HTTPS at an AWS Application Load Balancer with an ACM certificate. The workflow does not provision AWS infrastructure.

## Phase 5: database, authentication and S3

Copy `.env.example` to `.env`. SQLite is the default for local development if `DATABASE_URL` is omitted. For PostgreSQL, set `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME`. Set a long random `JWT_SECRET_KEY`; production refuses the development placeholder. Passwords are hashed with Argon2. Analysis, competitor research, report export, upload and history endpoints require `Authorization: Bearer <access_token>` after login.

To enable private object storage, create an S3 bucket with Block Public Access enabled, configure `AWS_REGION` and `AWS_S3_BUCKET`, and provide AWS credentials through an IAM role or the standard AWS credential chain. Grant the backend only required `s3:PutObject` and `s3:GetObject` permissions on the bucket/prefix. Objects are namespaced by user ID and uploads use SSE-S3. Report exports are archived to S3 when configured. Keep the bucket private; use the authenticated history endpoint for short-lived source download URLs.

For local setup, install requirements and start the backend; tables are created automatically for development. Production should use Alembic migrations, managed PostgreSQL, TLS, a secret manager, rate limiting, refresh-token/session revocation, email verification, backups and security monitoring before onboarding external customers. The frontend stores short-lived access tokens in localStorage in this capstone implementation; production should prefer secure HttpOnly cookies and a hardened CSP.

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
4. Phase 4 — PDF, DOCX and PPTX report generation (implemented).
5. Phase 5 — PostgreSQL, S3, authentication and analysis history (implemented; production hardening remains).
6. Phase 6 — Docker, AWS deployment, CI/CD and monitoring.
