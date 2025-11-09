from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.db.base import Base

# Import all models so that they are registered on the metadata before table creation
from app.models.company import Company
from app.models.chatbot import Chatbot
from app.models.chat import Chat
from app.models.visitor import Visitor
from app.models.visitor_session import VisitorSession


SQLALCHEMY_DATABASE_URL = get_settings().DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Create all tables (only for development; in production, use Alembic migrations)
def init_db():
    Base.metadata.create_all(bind=engine)
