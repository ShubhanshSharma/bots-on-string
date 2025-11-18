from fastapi import APIRouter
from . import company, chatbot, chat, visitor,upload_routes

router = APIRouter()
router.include_router(company.router, prefix="/company", tags=["Company"])
router.include_router(chatbot.router, prefix="/chatbot", tags=["Chatbot"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(visitor.router, prefix="/visitor", tags=["Visitor"])
router.include_router(upload_routes.router, prefix="/upload", tags=["upload"])
