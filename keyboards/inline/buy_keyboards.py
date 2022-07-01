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
            cur_name = lang_cur.rus if user.lang == 'ru' else lang_cur.eng
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
            name = lang_type.rus if user.lang == 'ru' else lang_type.eng
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=f"choice_pay_acc_buy_coin:{payment_type.uuid}"))
    back_text = await models.Lang.get(uuid="eef933b0-e3bc-46ed-8461-8226fd5f090f")
    keyboard.add(types.InlineKeyboardButton(text=back_text.rus if user.lang == 'ru' else back_text.eng, 
                                            callback_data="back_choice_currency_buy_coin"))
    return keyboard


async def choice_order_keboard(pay_type_serial_int: int, 
                               order_uuid: UUID,
                               user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    buy_text = await models.Lang.get(uuid="60a740c2-88f9-488a-8579-cb1fa2b1451a")
    keyboard.add(types.InlineKeyboardButton(text=buy_text.rus if user.lang == 'ru' else buy_text.eng, 
                                            callback_data=f"buy_order:{pay_type_serial_int}:{order_uuid}"))
    return keyboard


async def cancel_buy_order(order_uuid: UUID):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel_buy_order:{order_uuid}"))
    return keyboard


async def send_money_order(order_uuid: UUID, user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    cancel_text = await models.Lang.get(uuid="e1103afb-accd-472d-a707-1c5c70e55fe0")
    keyboard.add(types.InlineKeyboardButton(text=cancel_text.rus if user.lang == 'ru' else cancel_text.eng, 
                                            callback_data=f"cancel_buy_order:{order_uuid}"))
                                            # 778b75ff-0580-49d9-8b48-d41eb858bf59
    send_money_text = await models.Lang.get(uuid="778b75ff-0580-49d9-8b48-d41eb858bf59")
    keyboard.add(types.InlineKeyboardButton(text=send_money_text.rus if user.lang == 'ru' else send_money_text.eng, 
                                            callback_data=f"send_money_order:{order_uuid}"))
    return keyboard


async def go_to_buy_order_keyboard(order_uuid: UUID, user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    deal_text = await models.Lang.get(uuid="4ed8b02d-8577-42f3-8a85-67939b608fc6")
    keyboard.add(types.InlineKeyboardButton(text=deal_text.rus if user.lang == 'ru' else deal_text.eng, 
                                            callback_data=f"go_to_order:{order_uuid}"))
    return keyboard


async def keyboard_for_seller(order_uuid: UUID, 
                              user: models.User,
                              no_funds_button: bool = True):
    keyboard = types.InlineKeyboardMarkup()
    get_money_text = await models.Lang.get(uuid="d948631c-e9c3-44f1-9445-0ff1497b0ac0")
    keyboard.add(types.InlineKeyboardButton(text=get_money_text.rus if user.lang == 'ru' else get_money_text.eng, 
                                            callback_data=f"seller_approved_funds:{order_uuid}"))
    if no_funds_button:
        not_get_money_text = await models.Lang.get(uuid="76c4e43e-b207-4e33-8360-605de01080b5")
        keyboard.add(types.InlineKeyboardButton(text=not_get_money_text.rus if user.lang == 'rus' else not_get_money_text.eng, 
                                                callback_data=f"problem_seller_no_funds:{order_uuid}"))
    return keyboard

