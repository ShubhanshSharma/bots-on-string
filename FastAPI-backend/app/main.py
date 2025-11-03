# main.py
import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from app.core.database import Base, engine, SessionLocal
from app.api.api_v1.routes import router as api_router
from app.core.config import settings
from app.services.visitor_service import cleanup_expired_sessions_task
from app.db.session import engine, init_db
from app.db.base import Base
from app.api.api_v1.routes import router

load_dotenv()

app = FastAPI(title="T.R.I.B.E - TENANT RESOURCE INTELLIGENCE BOT ENSEMBLE")

# Create DB tables (simple approach: create_all). For production use alembic.
Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    # launch cleanup background task
    app.state.cleanup_task = asyncio.create_task(cleanup_expired_sessions_task())

@app.on_event("startup")
def on_startup():
    init_db()

@app.on_event("shutdown")
async def on_shutdown():
    task = getattr(app.state, "cleanup_task", None)
    if task:
        task.cancel()
@app.on_event("startup")
def on_startup():
    print("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

# Register routes
from app.api.api_v1.routes import router as api_router
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Backend running successfully 🚀"}

app.include_router(api_router)