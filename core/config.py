from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    smtp_from: str = os.getenv("SMTP_FROM", "")
    smtp_app_password: str = os.getenv("SMTP_APP_PASSWORD", "")
    smtp_to_override: str = os.getenv("SMTP_TO_OVERRIDE", "")

    resume_db_path: str = os.getenv("RESUME_DB_PATH", "vectorstore/resumes")
    jd_db_path: str = os.getenv("JD_DB_PATH", "vectorstore/jds")

    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

SETTINGS = Settings()
