from aiogram import types

from models import models
from utils.lang import lang_text

async def main_wallet_keyboard(user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    top_up_text = await models.Lang.get(uuid="69acb044-36b4-4b22-bdcf-a5bb6b1071aa")
    withdraw_text = await models.Lang.get(uuid="075ef4c1-8995-42d6-bde1-3f8c2e89da9e")
    keyboard.add(types.InlineKeyboardButton(text=top_up_text.rus if user.lang == 'ru' else top_up_text.eng,    
                                            callback_data="top_up"),
                 types.InlineKeyboardButton(text=withdraw_text.rus if user.lang == 'ru' else withdraw_text.eng, 
                                            callback_data="withdraw"))
    return keyboard


async def top_up_keyboard(user: models.User, code: str):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=await lang_text(lang_uuid="405671aa-89c6-4910-89a1-c6a7ede2e0cb", user=user), 
                                            url=f"ton://transfer/EQDcYqGh0d6i_kogT4QXvTuEq_iu61qPrZDVhbGnDvdrk-f3?text={code}"))
    return keyboard