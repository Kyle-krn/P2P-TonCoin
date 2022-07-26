from loader import dp
from aiogram import types
from models import models
from tortoise.queryset import Q
from utils import lang
from tortoise.exceptions import DoesNotExist
from handlers.start import start

@dp.message_handler(text="Схема работы")
@dp.message_handler(text="Scheme of work")
async def scheme_of_work_handler(message: types.Message):
    try:
        user = await models.User.get(telegram_id=message.chat.id)
    except DoesNotExist:
        return await start(message)
    await message.answer_document(document=types.InputFile('static/scheme_of_work.pdf'))
    problem_seller_order = await models.Order.get_or_none(state="need_admin_resolution", seller_id=user.uuid)
    format = None
    if problem_seller_order:
        format={"type_user": "продавцом" if user.lang == 'ru' else "seller"}
    problem_customer_order = await models.Order.get_or_none(state="need_admin_resolution", customer_id=user.uuid)
    if problem_customer_order:
        format={"type_user": "покупателем" if user.lang == 'ru' else "customer"}

    if format:
        text = await lang.lang_text(lang_uuid="35ef8f74-1c2f-4662-99f5-a12a8eb25081",
                                    user=user,
                                    format=format)
        await message.answer(text=text)