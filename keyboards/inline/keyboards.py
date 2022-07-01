from aiogram import types

from models import models


async def language_keyboard(user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    ru_button_text = await models.Lang.get(uuid="2615be7e-9735-4563-a97e-c003076d3bc6")
    eng_button_text = await models.Lang.get(uuid="3fc4161c-c306-4376-997b-b8929f699922")
    
    keyboard.add(types.InlineKeyboardButton(text=ru_button_text.rus if user.lang == 'ru' else ru_button_text.eng,
                                            callback_data="lang:ru"),
                 types.InlineKeyboardButton(text=eng_button_text.rus if user.lang == 'ru' else eng_button_text.eng, 
                                            callback_data="lang:en"))
    return keyboard


async def stop_state_keyboard(user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    cancel_text = await models.Lang.get(uuid="c116ece4-f278-4c91-a9af-b6c679803f20")
    keyboard.add(types.InlineKeyboardButton(text=cancel_text.rus if user.lang == 'ru' else cancel_text.eng, 
                                            callback_data="stop_state"))
    return keyboard
