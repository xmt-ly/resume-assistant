import os
from dotenv import load_dotenv

load_dotenv()

AI_PROXY_URL = os.getenv("AI_PROXY_URL", "http://127.0.0.1:15721")
AI_API_KEY = os.getenv("AI_API_KEY", "sk-placeholder")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/resume_assistant.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
SESSION_SECRET = os.getenv("SESSION_SECRET", "resume-assistant-secret-key")

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
