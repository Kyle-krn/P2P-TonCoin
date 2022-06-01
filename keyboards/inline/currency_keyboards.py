from models import models
from aiogram import types
from tortoise.queryset import Q

async def currency_keyboard(callback: str):
    keyboard = types.InlineKeyboardMarkup()
    # all_currency = await models.Currency.filter(Q(is_active=True))
    all_currency = await models.Currency.filter(Q(is_active=True) & Q(user_payment_account_type__is_active=True))
    for currency in set(all_currency):
        cur_name = currency.name
        lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
        if lang_cur:
            cur_name = lang_cur.rus
        keyboard.add(types.InlineKeyboardButton(text=cur_name, callback_data=f"{callback}:{currency.name}"))
    if callback == 'add_cur_pay_acc':
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data="back_my_pay_account"))
    elif callback == 'sell_coin_currency':
        keyboard.add(types.InlineKeyboardButton(text='Отмена', callback_data="stop_state"))
    return keyboard