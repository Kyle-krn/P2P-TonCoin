from models import models
from aiogram import types

async def currency_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    all_currency = await models.Currency.filter(is_active=True)
    for currency in all_currency:
        cur_name = currency.name
        lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
        if lang_cur:
            cur_name = lang_cur.rus
        keyboard.add(types.InlineKeyboardButton(text=cur_name, callback_data=f"currency:{currency.name}"))
    return keyboard