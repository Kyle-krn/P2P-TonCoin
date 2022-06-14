from aiogram import Dispatcher

from loader import dp
from .throttling import ThrottlingMiddleware
from .cancel_state import CancelStateMiddleware

if __name__ == "middlewares":
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(CancelStateMiddleware())
