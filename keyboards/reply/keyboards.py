from aiogram import types


async def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ref_button = types.KeyboardButton(text="Реферальная система")
    help_button = types.KeyboardButton(text="Схема Работы")
    wallet_button = types.KeyboardButton(text="Кошелек")
    sell_button = types.KeyboardButton(text="Продать Ton")
    keyboard.add(wallet_button, sell_button)
    return keyboard