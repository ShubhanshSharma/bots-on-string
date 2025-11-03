from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.db.session import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BOTS-ON-STRING API",
    description="A multi-company chatbot training and management platform",
    version="1.0.0",
)

# Allow CORS (frontend <-> backend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to BOTS-ON-STRING API 🚀"}
