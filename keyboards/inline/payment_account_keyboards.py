from aiogram import types
from models import models
from tortoise.queryset import Q


async def list_payment_account_keyboard(user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    user_payment_accounts = await models.UserPaymentAccount.filter(Q(user=user) & Q(is_active=True))
    for account in user_payment_accounts:
        type_account = await account.type
        name = type_account.name
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=type_account.uuid)
        if lang_type:
            name = lang_type.rus
        
        user_data_text = ""
        for k,v in account.data.items():
            user_data_text += f"{k}: {v}|"
        keyboard.add(types.InlineKeyboardButton(text=f"{name}|{user_data_text}", callback_data=f"view_pay_acc:{account.serial_int}"))    
    keyboard.add(types.InlineKeyboardButton(text="Добавить способ оплаты", callback_data="add_payment_account"))
    return keyboard


async def choice_payment_keyboard(callback: str, currency: models.Currency):
    keyboard = types.InlineKeyboardMarkup()
    currency_type_payments = await models.UserPaymentAccountType.filter(currency=currency)
    for type_payment in currency_type_payments:
        name = type_payment.name
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=type_payment.uuid)
        if lang_type:
            name = lang_type.rus
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=f"{callback}:{type_payment.serial_int}"))
    if callback == 'pay_type':
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="add_payment_account"))
    elif callback == 'sell_coin_pay_type':
        keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="sell_coin_back_choice_pay_acc"))
    return keyboard


async def pay_account_control_keyboard(payment_type_serial_int: int, payment_acc_serial_int: int):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Изменить данные", callback_data=f"change_pay_acc:{payment_type_serial_int}:{payment_acc_serial_int}"))
    keyboard.add(types.InlineKeyboardButton(text="Удалить способ оплаты", callback_data=f"del_pay_acc:{payment_acc_serial_int}"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data=f"back_my_pay_account"))
    return keyboard