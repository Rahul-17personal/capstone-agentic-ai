# Phase 5 — Identity, Persistence and Object Storage

## Delivered
- Account registration and login with Argon2 password hashes.
- Short-lived JWT access tokens and authenticated API dependencies.
- SQLAlchemy models for users and analysis records.
- Per-user history create/list/read/delete endpoints; ownership is enforced in database queries.
- SQLite for local development and PostgreSQL through psycopg in deployed environments.
- Authenticated S3 pitch upload endpoint, per-user object prefixes, SSE-S3 encryption.
- Optional S3 archive of generated PDF/DOCX/PPTX exports.
- Frontend registration/login, sign-out, saved history list and automatic history save after analysis.

## Environment
See backend/.env.example. For local development, leave DATABASE_URL unset to use SQLite. For PostgreSQL:
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
JWT_SECRET_KEY must be a unique long random secret. APP_ENV=production refuses the development placeholder.
For S3, configure AWS_REGION and AWS_S3_BUCKET and use an IAM role/credential chain. Keep Block Public Access enabled.

## API
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
- POST /api/v1/history
- GET /api/v1/history
- GET /api/v1/history/{id}
- DELETE /api/v1/history/{id}
- POST /api/v1/uploads/pitch
- Existing agent-workflow, competitive-research and reports endpoints now require bearer auth.

## Security notes
- Never commit .env or credentials.
- Use a private S3 bucket and least-privilege IAM role scoped to the bucket prefix.
- Access tokens are short-lived; refresh/revocation, MFA, email verification, login throttling, secure HttpOnly cookie transport, CSP and audit trails are production follow-ups.
- SQLAlchemy metadata create_all is used for capstone/dev bootstrapping. Use Alembic migrations for production schema evolution.
- The frontend currently stores the access token in localStorage; use secure HttpOnly cookies in a production browser deployment.
- Analysis history stores analysis JSON in the database. Original pitch files are not automatically persisted by the analysis endpoint; use the authenticated uploads endpoint when S3 is configured.
