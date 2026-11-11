import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    PROJECT_NAME: str = "Lead Shark"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "leadshark-super-secure-production-ready-jwt-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./leadshark.db")
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://leadshark.vercel.app",
        os.getenv("FRONTEND_URL", "http://localhost:5173")
    ]
    
    # Initial Admin / Seed accounts
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@leadshark.io")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "AdminLeadShark2026!")
    ADMIN_NAME: str = "LeadShark Admin"

    REVIEWER_EMAIL: str = os.getenv("REVIEWER_EMAIL", "reviewer@leadshark.io")
    REVIEWER_PASSWORD: str = os.getenv("REVIEWER_PASSWORD", "ReviewerLeadShark2026!")
    REVIEWER_NAME: str = "Compliance Reviewer"

    SALES_EMAIL: str = os.getenv("SALES_EMAIL", "sales@leadshark.io")
    SALES_PASSWORD: str = os.getenv("SALES_PASSWORD", "SalesLeadShark2026!")
    SALES_NAME: str = "Sales Representative"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    PORT: int = int(os.getenv("PORT", 8000))

    def get_database_url(self) -> str:
        # Render provides postgres:// which SQLAlchemy 1.4+ / 2.0 requires as postgresql://
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    def get_allowed_origins(self) -> List[str]:
        origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "https://leadshark.vercel.app"
        ]
        if self.FRONTEND_URL:
            clean = self.FRONTEND_URL.strip().rstrip("/")
            if clean and clean not in origins:
                origins.append(clean)
        extra = os.getenv("ADDITIONAL_CORS_ORIGINS")
        if extra:
            for o in extra.split(","):
                o_clean = o.strip().rstrip("/")
                if o_clean and o_clean not in origins:
                    origins.append(o_clean)
        return origins

settings = Settings()
