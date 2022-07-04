from __future__ import nested_scopes
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from handlers.cancel_state_handlers import cancel_state_message

RU_MAIN_BUTTON = ("Кошелек", "Реферальная система", "Схема Работы", "Продать Ton", "Купить Ton", "Мои счета", "Мои активные заказы", "Язык: ru")
ENG_MAIN_BUTTON = ("Wallet", "Sell Ton", "My bank account", "Buy Ton", "My active deals", "Referal system", "Language: eng", "Scheme of work")


class CancelStateMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        # print(await data['state'].get_state())
        if (message.text in RU_MAIN_BUTTON or message.text in ENG_MAIN_BUTTON) and await data['state'].get_state() is not None:
            await cancel_state_message(message, data['state'])
            raise CancelHandler()