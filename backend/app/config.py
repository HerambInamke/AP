import os

# Load .env if present (very small loader, no extra dependency)
_env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(_env_path):
    for line in open(_env_path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SECRET_KEY = os.getenv("SECRET_KEY", "ai-pulse-dev-secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aipulse.db")
AI_MODE = os.getenv("AI_MODE", "mock")  # "mock" or "live"
LLM_API_URL = os.getenv("LLM_API_URL", "")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")
TOKEN_HOURS = 12
APP_ENV = os.getenv("APP_ENV", "dev")  # "dev" | "production"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
# Client rule (Northwind): never show a group's results with fewer respondents than this
MIN_GROUP_SIZE = int(os.getenv("MIN_GROUP_SIZE", "5"))

if APP_ENV == "production" and SECRET_KEY == "ai-pulse-dev-secret":
    raise RuntimeError("Set SECRET_KEY before running in production")
