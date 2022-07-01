from fastapi import APIRouter
from .endpoint import lang

lang_router = APIRouter()


lang_router.include_router(lang.lang_bot_text_router)

