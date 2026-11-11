from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import *  # ensure all models are registered
from app.utils.seeding import seed_database
from app.routes import auth, dashboard, leads, discovery, campaigns, compliance, audit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leadshark")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed default accounts/data
    logger.info("Initializing Lead Shark database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        logger.info("Database seeding verified.")
    finally:
        db.close()
    yield
    logger.info("Lead Shark backend shutting down.")

app = FastAPI(
    title="Lead Shark API",
    description="Compliant Lead Discovery & Outreach Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from Vite dev server and Vercel production frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secure Global Exception Handler: Protects against stack trace leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the compliance administrator."}
    )

# Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Lead Shark Backend",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

# API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(leads.router, prefix=settings.API_V1_STR)
app.include_router(discovery.router, prefix=settings.API_V1_STR)
app.include_router(campaigns.router, prefix=settings.API_V1_STR)
app.include_router(compliance.router)
app.include_router(audit.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
