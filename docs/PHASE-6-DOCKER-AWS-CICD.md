# Phase 6 — Docker, AWS deployment and CI/CD

## What is included
- Multi-stage React/Vite frontend Docker image served by Nginx.
- Python 3.12 FastAPI backend image running as a non-root user.
- Docker Compose for local frontend + backend + PostgreSQL.
- Nginx serves the SPA and reverse-proxies /api/* to FastAPI.
- GitHub Actions CI: backend tests, frontend production build and Docker image builds.
- GitHub Actions deployment workflow: publish versioned images to GHCR and deploy to an EC2 host over SSH.
- Production Compose file expects managed PostgreSQL (RDS), private S3 and secrets supplied on the EC2 host.
- TLS is intended to terminate at an AWS Application Load Balancer with an ACM certificate. Do not expose the app container's port 80 directly to the public internet.

## Local Docker run
Prerequisites: Docker Desktop / Docker Engine with the Compose plugin.

1. Copy the root `.env.compose.example` to `.env`.
2. Copy `backend/.env.example` to `backend/.env`.
3. Put at least one model API key in `backend/.env`, and replace the JWT secret.
4. From the repository root:

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f backend
```

Open http://localhost:8080. Health endpoint: http://localhost:8080/api/v1/health.
Stop: `docker compose down`. To remove the local database volume too: `docker compose down -v` (this deletes local database data).

## AWS target topology
- Route 53 (optional DNS) points the application hostname to an Application Load Balancer.
- ACM certificate is attached to the ALB HTTPS listener (443).
- ALB forwards to the EC2 instance target group on TCP 80.
- EC2 security group allows inbound TCP 80 only from the ALB security group; SSH 22 should be restricted to an administrator IP or replaced with SSM Session Manager.
- EC2 runs the frontend and backend containers with Docker Compose.
- RDS PostgreSQL is private, and its security group allows TCP 5432 only from the EC2 security group.
- S3 bucket has Block Public Access enabled; EC2 instance profile grants only required access to the PitchIntel object prefix.
- CloudWatch receives EC2/container logs and host metrics. Configure alarms for instance health, CPU, disk and ALB 5xx/target health.

## EC2 preparation
Use a supported Linux AMI and install Docker Engine + Docker Compose plugin. Create an application directory, for example `/opt/pitchintel`, with:
- `/opt/pitchintel/docker-compose.yml` copied from `docker-compose.prod.yml` by the deploy workflow.
- `/opt/pitchintel/.env` containing `FRONTEND_ORIGIN=https://pitchintel.example.com`.
- `/opt/pitchintel/backend/.env` containing the application secrets and service configuration.

Example backend environment (do not commit real values):

```env
APP_ENV=production
OPENAI_API_KEY=...
GEMINI_API_KEY=...
TAVILY_API_KEY=...
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@RDS_ENDPOINT:5432/pitchintel
JWT_SECRET_KEY=<long-random-secret>
ACCESS_TOKEN_MINUTES=60
AWS_REGION=ap-south-1
AWS_S3_BUCKET=<private-bucket-name>
FRONTEND_ORIGIN=https://pitchintel.example.com
```

Create the RDS database and user before deploying. Configure S3 and the EC2 instance profile before enabling uploads. The app currently creates SQLAlchemy tables on startup for capstone convenience; move to Alembic migrations before production schema changes.

## GitHub repository secrets required for deployment
- `EC2_HOST`: public DNS name or IP of the EC2 host.
- `EC2_USER`: SSH login user (for example, ubuntu or ec2-user).
- `EC2_SSH_PRIVATE_KEY`: private key matching an authorized EC2 SSH key.
- `EC2_APP_DIR`: deployment directory (for example, /opt/pitchintel).
- `GHCR_USERNAME`: GitHub username with package read access.
- `GHCR_READ_TOKEN`: fine-grained/classic PAT with read:packages for the private GHCR images.

The GitHub Actions workflow publishes the backend and frontend images to GitHub Container Registry. It deploys automatically on pushes to `main`, or can be run manually with workflow_dispatch. Protect `main` and require CI checks before merging. Configure GHCR package permissions so the token can pull both images.

## CI/CD behavior
- Pull requests to main: run backend tests, frontend build, and Docker build checks.
- Pushes to main and Phase 6 feature branches: run CI checks.
- Pushes to main: publish `latest` and commit-SHA image tags, then update EC2 Compose services.
- Deployment requires the repository secrets above and pre-provisioned AWS resources. It does not create VPC, ALB, ACM, RDS, S3 or EC2 resources automatically.

## Operational checklist
- Use HTTPS at the ALB and redirect HTTP to HTTPS.
- Keep RDS and S3 private; enable RDS encryption, backups and deletion protection.
- Store secrets only on the host or in AWS Secrets Manager/SSM Parameter Store; never commit .env files.
- Use an EC2 instance profile rather than static AWS access keys.
- Restrict security groups and SSH access; prefer SSM Session Manager.
- Configure log rotation, CloudWatch alarms, backups and a rollback procedure.
- Set CORS `FRONTEND_ORIGIN` to the exact public HTTPS origin.
- The deployment workflow has not been run against an actual AWS account. Validate in a staging environment before production traffic.
