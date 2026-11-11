from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent_routes import router as agent_router
from app.api.competitive_routes import router as competitive_router
from app.api.report_routes import router as report_router
from app.api.auth_routes import router as auth_router
from app.api.history_routes import router as history_router
from app.api.upload_routes import router as upload_router
from app.db import Base, engine
import app.models  # noqa: F401
from app.api.routes import router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Sales Pitch Review and Competitive Intelligence",
    version="0.4.0",
)
if settings.APP_ENV == "production" and settings.JWT_SECRET_KEY == "dev-only-change-this-secret-before-deploying":
    raise RuntimeError("Set a secure JWT_SECRET_KEY before production startup")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1", tags=["Pitch Analysis"])
app.include_router(agent_router, prefix="/api/v1", tags=["Agentic Workflow"])
app.include_router(competitive_router, prefix="/api/v1", tags=["Competitive Intelligence"])
app.include_router(report_router, prefix="/api/v1", tags=["Report Export"])
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(history_router, prefix="/api/v1", tags=["Analysis History"])
app.include_router(upload_router, prefix="/api/v1", tags=["File Uploads"])


@app.get("/")
def root():
    return {"message": "Welcome to PitchIntel AI", "version": app.version}
