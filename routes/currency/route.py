from fastapi import APIRouter
from .endpoint import get_currency, post_currency

currency_router = APIRouter()

currency_router.include_router(get_currency.get_currency_router)
currency_router.include_router(post_currency.post_currency_router)
