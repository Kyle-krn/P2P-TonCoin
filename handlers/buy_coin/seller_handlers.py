from loader import dp, bot
from aiogram import types
from models import models
from datetime import datetime


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'seller_approved_funds')
async def seller_approved_funds_handler(call: types.CallbackQuery):
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state not in ['buyer_sent_funds', 'problem_seller_no_funds', 'need_admin_resolution']:
        return await call.message.edit_text("Не подходит state")
    seller = await order.seller
    customer = await order.customer
    customer.balance += (order.amount - order.commission)
    seller.frozen_balance -= order.amount
    order.state = "done"
    payment_operation = await order.payment_operation.all().first()
    payment_operation.state = "success"
    await payment_operation.save()
    await order.save()
    await seller.save()
    await customer.save()
    seller_text = await models.Lang.get(uuid="5c6ef30b-0802-4ea9-a647-39ca776fa845")
    seller_text = seller_text.rus if seller.lang == 'ru' else seller_text.eng
    # seller_text = "Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом"
    customer_text = await models.Lang.get(uuid="02d0faf7-fc2f-420c-bac4-d7642546b903")
    customer_text = customer_text.rus if customer.lang == 'ru' else customer_text.eng
    customer_text = customer_text.format(uuid=order.uuid, balance=customer.balance)
    # customer_text = f"Продавец подтвердил получение ваших денежных средств по заказу № {order.uuid} TON отправлены на ваш кошелек"  \
    #                 f"Ваш баланс: {customer.balance} TON"
    await bot.send_message(seller.telegram_id, text=seller_text)
    await bot.send_message(customer.telegram_id, text=customer_text)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'problem_seller_no_funds')
async def problem_seller_no_funds_handler(call: types.CallbackQuery):
    date = call.message.date
    user = await models.User.get(telegram_id=call.message.chat.id)
    if (datetime.now() - date).total_seconds() < (4 * 60):
        text = await models.Lang.get(uuid="9bb9512f-c110-4044-a2c2-4b69025b4d53")
        text = text.rus if user.lang == 'ru' else text.eng
        # text = "Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем."
        return await call.message.answer(text)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    await call.message.edit_text("Средства не поступили")
    text = await models.Lang.get(uuid="41b82275-1cf9-45c0-bc03-54c265c5c960")
    text = text.rus if user.lang == 'ru' else text.eng
    # text = "Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам."
    await call.message.answer(text)
    payment_operation = await order.payment_operation.all().first()
    payment_operation.state = "disputed"
    order.state = "problem_seller_no_funds"
    await order.save()
    await payment_operation.save()
    customer = await order.customer
    text = await models.Lang.get(uuid="ce92fb9e-53e2-4f72-93ab-cf337af076f8")
    text = text.rus if customer.lang == 'ru' else text.eng
    # text = "Продавец сообщил, что не получил оплату от вас."  \
    #        "Пришлите, пожалуйста, подтверждение оплаты (чек)"  \
    #        "в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение."  \
    #        "Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен"
    await bot.send_message(chat_id=customer.telegram_id, 
                           text=text)



