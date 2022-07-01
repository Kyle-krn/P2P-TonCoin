from models import models
from aiogram import types
from tortoise.queryset import Q

async def currency_keyboard(callback: str, user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    # all_currency = await models.Currency.filter(Q(is_active=True))
    all_currency = await models.Currency.filter(Q(is_active=True) & Q(user_payment_account_type__is_active=True))
    for currency in set(all_currency):
        cur_name = currency.name
        lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
        if lang_cur:
            cur_name = lang_cur.rus if user.lang == 'ru' else lang_cur.eng
        keyboard.add(types.InlineKeyboardButton(text=cur_name, callback_data=f"{callback}:{currency.name}"))
    if callback == 'add_cur_pay_acc':
        back_text = await models.Lang.get(uuid="eef933b0-e3bc-46ed-8461-8226fd5f090f")
        keyboard.add(types.InlineKeyboardButton(text=back_text.rus if user.lang == 'ru' else back_text.eng, 
                                                callback_data="back_my_pay_account"))
    elif callback == 'sell_coin_currency':
        cancel_text = await models.Lang.get(uuid="c116ece4-f278-4c91-a9af-b6c679803f20")
        keyboard.add(types.InlineKeyboardButton(text=cancel_text.rus if user.lang == 'ru' else cancel_text.eng, 
                                                callback_data="stop_state"))
    return keyboard