# Phase 2 — LangGraph Agentic Workflow

## Goal
Add a multi-agent workflow to the Phase 1 PitchIntel AI application while preserving the existing `POST /api/v1/analyze` endpoint.

## Workflow
1. **Strategist** — evaluates positioning, value proposition, target audience, differentiators and available proof.
2. **Critic** — independently evaluates messaging, strengths, weaknesses, missing information and risk flags.
3. **Sales Coach** — creates prioritised recommendations and a rewritten pitch, without inventing proof.
4. **Report Synthesizer** — validates and consolidates agent outputs into the existing `PitchAnalysis` response contract.

LangGraph owns the state transitions. The current workflow is intentionally sequential so later agents can use earlier findings. A later iteration can add parallel branches, human approval checkpoints and retry policies.

## API
`POST /api/v1/agent-workflow`

Multipart fields:
- `file`: PDF, DOCX or PPTX
- `provider`: `openai` or `gemini`
- `competitors`: optional comma-separated names

The response contains the Phase 1 `analysis` object and a `workflow` object listing completed agents.

## Install and run
From `backend/`:
```bash
pip install -r requirements-phase2.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Set the selected provider key in `.env`. Never put provider keys in frontend code or commit a real `.env` file.

## Test
```bash
pytest
```

The workflow unit test stubs the provider adapter; it does not require live API credentials. Live provider tests require valid API keys and may incur usage charges.

## Current scope and limitations
- Competitor names are passed as context only. This phase does not perform live web research or claim current competitor facts.
- The current graph runs agents sequentially and makes one model call per agent.
- Uploads are temporary and removed after processing.
- Scanned/image-only PDFs and slide images are not OCR-processed.
- Production hardening (authentication, quotas, malware scanning, persistent audit history, retries/timeouts and observability) remains future work.
