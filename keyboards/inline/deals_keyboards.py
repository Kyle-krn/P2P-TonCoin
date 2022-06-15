from typing import List
from aiogram import types
from models import models

async def show_deals_keyboard(orders: List[models.Order], page: int, last_page: int):
    keyboard = types.InlineKeyboardMarkup()
    for order in orders:
        text = f"№{order.serial_int + 5432}|{order.amount} TON|"
        if order.state == "created":
            text += "Создано"
        elif order.state == "ready_for_sale":
            text += "Ожидает покупателя"
        elif order.state == "wait_buyer_send_funds":
            text += "Ожидает оплату от покупателя"
        elif order.state == "buyer_sent_funds":
            text += "Ожидает подтверждения средств на ваш счет"
        elif order.state == "problem_seller_no_funds":
            text += "Проблема с поступлением средств"
        elif order.state == "need_admin_resolution":
            text += "Ожидает решения администрации"
        
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"view_order:{order.uuid}"))
    
    prev_button = types.InlineKeyboardButton(text="⬅️", callback_data=f"order_pagination:{page-1}")
    now_button = types.InlineKeyboardButton(text=f"{page}/{last_page}📄", callback_data=f"s")
    next_button = types.InlineKeyboardButton(text="➡️", callback_data=f"order_pagination:{page+1}")

    pagination_list = []
    if page > 1:
        pagination_list.append(prev_button)
    pagination_list.append(now_button)
    if last_page != page:
        pagination_list.append(next_button)
    keyboard.add(*pagination_list)
    return keyboard


async def cancel_order_keyboard(order_uuid):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel_order:{order_uuid}"))
    return keyboard


async def created_order_keyboard(order_uuid):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel_order:{order_uuid}"))
    keyboard.add(types.InlineKeyboardButton(text="Внести средства", callback_data=f"add_pay_acc_in_created:{order_uuid}"))
    return keyboard
