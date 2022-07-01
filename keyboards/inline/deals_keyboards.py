from typing import List
from uuid import UUID
from aiogram import types
from models import models

async def show_deals_keyboard(orders: List[models.Order], 
                              page: int, 
                              last_page: int,
                              user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    for order in orders:
        text = f"№{order.serial_int}|{order.amount} TON|"
        if order.state == "created":
            created_text = await models.Lang.get(uuid="e8f93b03-16f6-4675-94e1-9e36c66ce943")
            text += created_text.rus if user.lang == 'ru' else created_text.eng
        elif order.state == "ready_for_sale":
            wait_buyer_text = await models.Lang.get(uuid="4aa099f5-06c5-4400-9ff4-63afd0688202")
            text += wait_buyer_text.rus if user.lang == 'ru' else wait_buyer_text.eng
        elif order.state == "wait_buyer_send_funds":
            wait_money_text = await models.Lang.get(uuid="67beaccf-d10f-4c0d-9c6f-6d4f476dedb5")
            text += wait_money_text.rus if user.lang == 'ru' else wait_money_text.eng
        elif order.state == "buyer_sent_funds":
            wait_confirm_text = await models.Lang.get(uuid="4edb3d5a-bfc6-4834-94a6-81d0e0b41207")
            text += wait_confirm_text.rus if user.lang == 'ru' else wait_confirm_text.eng
        elif order.state == "problem_seller_no_funds":
            funding_problem_text = await models.Lang.get(uuid="3fe0644c-af1e-466c-bad9-0c53e1fd84ef")
            text += funding_problem_text.rus if user.lang == 'ru' else funding_problem_text.eng
        elif order.state == "need_admin_resolution":
            manager_text = await models.Lang.get(uuid="3989b0e3-0631-4429-bd99-3fbac9a59b3a")
            text += manager_text.rus if user.lang == 'ru' else manager_text.eng
        
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=f"view_order:{order.uuid}"))
    
    prev_text = await models.Lang.get(uuid="f49402b2-f81a-4daa-9181-5031f435b8aa")
    prev_button = types.InlineKeyboardButton(text=prev_text.rus if user.lang == 'ru' else prev_text.eng, callback_data=f"order_pagination:{page-1}")
    now_text = await models.Lang.get(uuid="6d821da8-34f1-410b-8df6-aa1c7447ef5a")
    now_text = now_text.rus if user.lang == 'ru' else now_text.eng
    now_text = now_text.format(page=page, last_page=last_page)
    now_button = types.InlineKeyboardButton(text=now_text, callback_data=f"s")
    next_text = await models.Lang.get(uuid="4ba02a78-90a7-4a71-9c21-292098e1456c")
    next_button = types.InlineKeyboardButton(text=next_text.rus if user.lang == 'ru' else next_text.eng, callback_data=f"order_pagination:{page+1}")

    pagination_list = []
    if page > 1:
        pagination_list.append(prev_button)
    pagination_list.append(now_button)
    if last_page != page:
        pagination_list.append(next_button)
    keyboard.add(*pagination_list)
    return keyboard


async def cancel_order_keyboard(order_uuid: UUID, user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    cancel_text = await models.Lang.get(uuid="e1103afb-accd-472d-a707-1c5c70e55fe0")
    keyboard.add(types.InlineKeyboardButton(text=cancel_text.rus if user.lang == 'ru' else cancel_text.eng, callback_data=f"cancel_order:{order_uuid}"))
    return keyboard


async def created_order_keyboard(order_uuid: UUID, user: models.User):
    keyboard = types.InlineKeyboardMarkup()
    cancel_text = await models.Lang.get(uuid="e1103afb-accd-472d-a707-1c5c70e55fe0")
    keyboard.add(types.InlineKeyboardButton(text=cancel_text.rus if user.lang == 'ru' else cancel_text.eng, callback_data=f"cancel_order:{order_uuid}"))
    
    deposit_text = await models.Lang.get(uuid="a71cd1a0-5624-454d-9213-850196ea13b6")
    keyboard.add(types.InlineKeyboardButton(text=deposit_text.rus if user.lang == 'ru' else deposit_text.eng, 
                                            callback_data=f"add_pay_acc_in_created:{order_uuid}"))
    return keyboard
