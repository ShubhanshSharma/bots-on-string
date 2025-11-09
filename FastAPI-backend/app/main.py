# main.py
import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app.api.api_v1.routes import router as api_router
from app.core.config import get_settings
from app.services.visitor_service import cleanup_expired_sessions_task
from app.db.session import engine, init_db
from app.db.base import Base

load_dotenv()
settings=get_settings()
app = FastAPI(title="T.R.I.B.E - TENANT RESOURCE INTELLIGENCE BOT ENSEMBLE")
Base.metadata.create_all(bind=engine)

# ✅ Allow frontend origin
origins = [
    "http://localhost:3000",   # Next.js dev server
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create DB tables (simple approach: create_all). For production use alembic.

@app.on_event("startup")
async def on_startup():
    # launch cleanup background task
    app.state.cleanup_task = asyncio.create_task(cleanup_expired_sessions_task())

@app.on_event("startup")
async def on_startup():
    # Create tables (for dev only). Use alembic in prod.
    print("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    # Start background cleanup task (if needed)
    app.state.cleanup_task = asyncio.create_task(cleanup_expired_sessions_task())

@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "cleanup_task", None)
    if task:
        task.cancel()

app.include_router(api_router)
# Register routes
from app.api.api_v1.routes import router as api_router

@app.get("/")
def root():
    return {"message": "Backend running successfully 🚀"}
