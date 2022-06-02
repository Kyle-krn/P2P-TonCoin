import os
from loader import dp, bot, BASE_DIR
from aiogram import types
from models import models
from tortoise.queryset import Q

ALLOWED_TYPES = ("pdf" , "xls" , "xcls" , "jpg" , "pdf" ,"gif")

@dp.message_handler(content_types=['photo', 'document'])
async def pruf_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    problem_order = await models.Order.get_or_none(customer=user, state="problem_seller_no_funds")
    if not problem_order:
        return
    
    problem_order_dir_path = "/static/problem_order/"
    if os.path.exists(BASE_DIR + problem_order_dir_path) is False:
        os.mkdir(BASE_DIR + problem_order_dir_path)
    if message.photo:
        await message.photo[-1].download(BASE_DIR + problem_order_dir_path + f"{problem_order.uuid}.jpg")
        file_path = problem_order_dir_path + f"{problem_order.uuid}.jpg"
    elif message.document:
        file_type = message.document.file_name.split('.')[-1]
        if file_type.lower() not in ALLOWED_TYPES:
            text = "Неверный формат подтверждения оплаты."  \
                   "Пришлите, пожалуйста, подтверждение оплаты"  \
                   "(чек) в формате pdf / xls / xcls / jpg / pdf / gif"  \
                   " в ответ на это сообщение. Если вы не пришлете подтверждение"  \
                   " в течение 24 часов, то заказ будет автоматически отменен."
            return await message.answer(text)
        await message.document.download(BASE_DIR + problem_order_dir_path + f"{problem_order.uuid}.{file_type}")
        file_path = BASE_DIR + problem_order_dir_path + f"{problem_order.uuid}.{file_type}"
    await models.ProblemOrderProof.create(order=problem_order, file_path=file_path)
    text = "Спасибо! Мы инициировали разбирательство по заказу. В течение 24 часов вы получите ответ"
    await message.answer(text)
    problem_order.state = "need_admin_resolution"
    await problem_order.save()
    await models.Order.filter(Q(seller=await problem_order.seller) & Q(state="ready_for_sale")).update(state="created")

