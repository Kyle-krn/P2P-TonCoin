from aiogram import types

async def main_wallet_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Пополнить", callback_data="top_up"),
                 types.InlineKeyboardButton(text="Вывести", callback_data="withdraw"))
    return keyboard