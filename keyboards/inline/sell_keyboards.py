from aiogram import types
from models import models
from typing import List

async def add_pay_account_keyboard(user_payment_accounts: List[models.UserPaymentAccount]):
    keyboard = types.InlineKeyboardMarkup()
    for account in user_payment_accounts:
        type_account = await account.type
        name = type_account.name
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=type_account.uuid)
        if lang_type:
            name = lang_type.rus
        user_data_text = ""
        for k,v in account.data.items():
            user_data_text += f"{k}: {v} "
        keyboard.add(types.InlineKeyboardButton(text=f"{name} {user_data_text}", callback_data=f"sell_coin_choice_pay_acc:{account.serial_int}"))
    if len(user_payment_accounts) > 0:
        keyboard.add(types.InlineKeyboardButton(text="Выбрать все", callback_data="sell_coin_choice_pay_acc:all"))    
    keyboard.add(types.InlineKeyboardButton(text="Добавить способ оплаты", callback_data="sell_coin_add_pay_acc"))
    
    return keyboard