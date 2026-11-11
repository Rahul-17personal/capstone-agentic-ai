import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")
load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "PitchIntel AI")
    APP_ENV = os.getenv("APP_ENV", "development")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or None
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or None
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "openai").lower()
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "20"))
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


settings = Settings()
