"""
FastAPI application entry point for AI-CRM-HCP.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.database import init_db
from app.api.interactions import router as interactions_router
from app.api.doctors import router as doctors_router
from app.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup: create database tables
    init_db()
    print("[OK] Database tables created/verified")
    print("[OK] AI-CRM-HCP API is ready")
    yield
    # Shutdown
    print("[STOP] Shutting down AI-CRM-HCP API")


app = FastAPI(
    title="AI-CRM-HCP API",
    description=(
        "AI-powered CRM for pharmaceutical sales representatives. "
        "Features LangGraph agent with 5 tools for intelligent interaction management."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(interactions_router)
app.include_router(doctors_router)
app.include_router(chat_router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI-CRM-HCP API",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/api/seed", tags=["Setup"])
def trigger_seed():
    """Temporary endpoint to seed the database."""
    from app.utils.seed import seed_database
    try:
        seed_database()
        return {"status": "success", "message": "Database seeded with sample data!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "agent": "ready",
    }
