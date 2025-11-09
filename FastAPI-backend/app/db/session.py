from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.db.base import Base

# ✅ Import all models so they're registered with SQLAlchemy metadata
import app.models.visitor
import app.models.visitor_session
import app.models.company
import app.models.chatbot
import app.models.chat

SQLALCHEMY_DATABASE_URL = get_settings().DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ This function will create all tables when the app starts
def init_db():
    Base.metadata.create_all(bind=engine)
