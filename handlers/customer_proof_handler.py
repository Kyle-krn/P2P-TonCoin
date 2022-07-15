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
            text = await models.Lang.get(uuid="cb5de656-c423-4e0c-a5a7-e8c07b3891ce")
            text = text.rus if user.lang == 'ru' else text.eng
            # text = "Неверный формат подтверждения оплаты. Пришлите, пожалуйста, подтверждение оплаты (чек) в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение. Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен."
            return await message.answer(text)
        await message.document.download(BASE_DIR + problem_order_dir_path + f"{problem_order.uuid}.{file_type}")
        file_path = BASE_DIR + problem_order_dir_path + f"{problem_order.uuid}.{file_type}"
    await models.ProblemOrderProof.create(order=problem_order, file_path=file_path)
    text = await models.Lang.get(uuid="419722a1-70a0-430a-a2e0-033f17245ba0")
    text = text.rus if user.lang == 'ru' else text.eng
    # text = "Спасибо! Мы инициировали разбирательство по заказу. В течение 24 часов вы получите ответ"
    await message.answer(text)
    await models.OrderStateChange.create(order=problem_order, 
                                         old_state=problem_order.state, 
                                         new_state="need_admin_resolution")
    problem_order.state = "need_admin_resolution"
    await problem_order.save()
    orders = await models.Order.filter(Q(seller=await problem_order.seller) & Q(state="ready_for_sale"))
    for order in orders:
        await models.OrderStateChange.create(order=order, 
                                             old_state=order.state, 
                                             new_state="suspended")
        order.state = "suspended"
        await order.save()

