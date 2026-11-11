from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Sales Pitch Review and Competitive Intelligence",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api/v1", tags=["Pitch Analysis"])


@app.get("/")
def root():
    return {"message": "Welcome to PitchIntel AI", "version": app.version}
