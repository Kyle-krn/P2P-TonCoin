from uuid import UUID
from aiogram import types
from models import models
from tortoise.queryset import Q

async def currency_keyboard(user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    curency_list = await models.Currency.filter(orders__state="ready_for_sale").exclude(orders__seller=user)
    for currency in set(curency_list):
        cur_name = currency.name
        lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
        if lang_cur:
            cur_name = lang_cur.rus
        keyboard.add(types.InlineKeyboardButton(text=cur_name, callback_data=f"choice_currency_buy_coin:{currency.uuid}"))
    return keyboard


async def payment_type_keyboard(user: models.User, currency_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    query = Q(payments_account__order_user_payment_account__order__state="ready_for_sale") & Q(payments_account__order_user_payment_account__order__currency__uuid=currency_uuid)
    payments_type_list = await models.UserPaymentAccountType.filter(query).exclude(payments_account__order_user_payment_account__order__seller=user)
    for payment_type in set(payments_type_list):
        name = payment_type.name
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=payment_type.uuid)
        if lang_type:
            name = lang_type.rus
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=f"choice_pay_acc_buy_coin:{payment_type.uuid}"))
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_choice_currency_buy_coin"))
    return keyboard


async def choice_order_keboard(pay_type_serial_int: int, order_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Купить", callback_data=f"buy_order:{pay_type_serial_int}:{order_uuid}"))
    return keyboard


async def cancel_buy_order(order_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel_buy_order:{order_uuid}"))
    return keyboard


async def send_money_order(order_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel_buy_order:{order_uuid}"))
    keyboard.add(types.InlineKeyboardButton(text="Я отправил средства", callback_data=f"send_money_order:{order_uuid}"))
    return keyboard


async def go_to_buy_order_keyboard(order_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Перейти к седлке", callback_data=f"go_to_order:{order_uuid}"))
    return keyboard


async def keyboard_for_seller(order_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Я получил средства", callback_data=f"seller_approved_funds:{order_uuid}"))
    keyboard.add(types.InlineKeyboardButton(text="Средства не поступили", callback_data=f"problem_seller_no_funds:{order_uuid}"))
    return keyboard

