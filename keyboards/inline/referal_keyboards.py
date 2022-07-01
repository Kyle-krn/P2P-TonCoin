from uuid import UUID
from aiogram import types
from models import models

async def referal_keyboard(user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    ref_text = await models.Lang.get(uuid="ee766ac7-47f1-47be-b5eb-f8f3a8c2fcd6")
    keyboard.add(types.InlineKeyboardButton(text=ref_text.rus if user.lang == 'ru' else ref_text.eng, 
                                            url=f"https://t.me/share/url?url=https://t.me/TonCoinTestBot?start={user.uuid}"))
    return keyboard