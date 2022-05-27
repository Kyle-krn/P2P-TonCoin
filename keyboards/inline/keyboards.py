from aiogram import types


async def language_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
                 types.InlineKeyboardButton(text="English", callback_data="lang:eng"))
    return keyboard
