from aiogram import types


async def language_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Русский", callback_data="lang:ru"),
                 types.InlineKeyboardButton(text="English", callback_data="lang:eng"))
    return keyboard


async def stop_state_keyboard():
    # 
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отмена", callback_data="stop_state"))
    return keyboard
