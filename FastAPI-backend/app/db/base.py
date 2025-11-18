from app.db.base_class import Base  # only import Base
from app.models.visitor import Visitor
from app.models.visitor_session import VisitorSession
from app.models.chatbot import Chatbot
from app.models.chat import Chat


from app.db.base_class import Base
from app.models.company import Company
from app.models.chatbot import Chatbot
# import all models here so Alembic can detect them
