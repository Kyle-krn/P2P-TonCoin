from typing import List
from aiogram import types
from models import models

async def show_deals_keyboard(orders: List[models.Order]):
    keyboard = types.InlineKeyboardMarkup()
    for order in orders:
        text = f"{order.amount} TON от {order.created_at.strftime('%d.%m.%y')}"
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"view_order:{order.uuid}"))
    return keyboard


async def cancel_order_keyboard(order_uuid):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data=f"cancel_order:{order_uuid}"))
    return keyboard