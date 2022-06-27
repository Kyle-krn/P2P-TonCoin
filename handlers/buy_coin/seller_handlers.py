from loader import dp, bot
from aiogram import types
from models import models
from datetime import datetime


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'seller_approved_funds')
async def seller_approved_funds_handler(call: types.CallbackQuery):
    '''Продавец подтверждает перевод средств'''
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state not in ['buyer_sent_funds', 'problem_seller_no_funds', 'need_admin_resolution']:
        return await call.message.edit_text("Не подходит state")
    seller = await order.seller
    customer = await order.customer
    customer.balance += (order.amount - order.commission)
    seller.frozen_balance -= order.amount
    await models.OrderStateChange.create(order=order, old_state=order.state, new_state="done")
    order.state = "done"
    payment_operation = await order.payment_operation.all().first()
    payment_operation.state = "success"
    await payment_operation.save()
    await order.save()
    await seller.save()
    await customer.save()
    seller_text = await models.Lang.get(uuid="36243794-383e-4c93-a1c6-fe9a0dafe54a")
    seller_text = seller_text.rus if seller.lang == 'ru' else seller_text.eng
    # seller_text = "Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом"
    customer_text = await models.Lang.get(uuid="02d0faf7-fc2f-420c-bac4-d7642546b903")
    customer_text = customer_text.rus if customer.lang == 'ru' else customer_text.eng
    customer_text = customer_text.format(uuid=order.serial_int, balance=customer.balance)
    # customer_text = f"Продавец подтвердил получение ваших денежных средств по заказу № {order.uuid} TON отправлены на ваш кошелек"  \
    #                 f"Ваш баланс: {customer.balance} TON"
    await call.message.delete()
    await bot.send_message(seller.telegram_id, text=seller_text)
    await bot.send_message(customer.telegram_id, text=customer_text)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'problem_seller_no_funds')
async def problem_seller_no_funds_handler(call: types.CallbackQuery):
    '''Продавец сообщает о том что средства не поступили'''
    date = call.message.date
    user = await models.User.get(telegram_id=call.message.chat.id)
    if (datetime.now() - date).total_seconds() < (4 * 60):
        text = await models.Lang.get(uuid="fa34de05-0e16-421a-b563-b939bd0d89af")
        text = text.rus if user.lang == 'ru' else text.eng
        # text = "Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем."
        return await call.message.answer(text)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state not in ("buyer_sent_funds", "wait_buyer_send_funds"):
        return await call.message.edit_text("Не подходит state")
    await call.message.edit_text("Средства не поступили")
    text = await models.Lang.get(uuid="9b7fbd7c-ba72-4de8-bb4c-c41c0628cd0b")
    text = text.rus if user.lang == 'ru' else text.eng
    # text = "Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам."
    await call.message.answer(text)
    payment_operation = await order.payment_operation.all().first()
    payment_operation.state = "disputed"
    await models.OrderStateChange.create(order=order, old_state=order.state, new_state="problem_seller_no_funds")
    order.state = "problem_seller_no_funds"
    await order.save()
    await payment_operation.save()
    customer = await order.customer
    text = await models.Lang.get(uuid="922417b3-1220-47c1-83ab-df140eda8f19")
    text = text.rus if customer.lang == 'ru' else text.eng
    # text = "Продавец сообщил, что не получил оплату от вас."  \
    #        "Пришлите, пожалуйста, подтверждение оплаты (чек)"  \
    #        "в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение."  \
    #        "Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен"
    await bot.send_message(chat_id=customer.telegram_id, 
                           text=text)