from aiogram import types
from models import models
from typing import List

async def add_pay_account_keyboard(user_payment_accounts: List[models.UserPaymentAccount], user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    for account in user_payment_accounts:
        type_account = await account.type
        name = type_account.name
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=type_account.uuid)
        if lang_type:
            name = lang_type.rus if user.lang == 'ru' else lang_type.eng
        user_data_text = ""
        for k,v in account.data.items():
            user_data_text += f"{k}: {v} "
        keyboard.add(types.InlineKeyboardButton(text=f"{name} {user_data_text}", callback_data=f"sell_coin_choice_pay_acc:{account.serial_int}"))
    if len(user_payment_accounts) > 0:
        select_all_text = await models.Lang.get(uuid="714f9df6-1b0a-446b-a462-cbaa2e8fe19d")
        keyboard.add(types.InlineKeyboardButton(text=select_all_text.rus if user.lang == 'ru' else select_all_text.eng, 
                                                callback_data="sell_coin_choice_pay_acc:all"))    
    
    append_payments_text = await models.Lang.get(uuid="2b2ade30-9570-4f42-a955-e21ff25ae5b2")
    keyboard.add(types.InlineKeyboardButton(text=append_payments_text.rus if user.lang == 'ru' else append_payments_text.eng, 
                                            callback_data="sell_coin_add_pay_acc"))
    
    return keyboard