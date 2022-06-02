from loader import dp, bot
from aiogram import types
from models import models
from datetime import datetime, timedelta

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'seller_approved_funds')
async def seller_approved_funds_handler(call: types.CallbackQuery):
    # сделать перерасчет  commission для созданных заказов
    order = await models.Order.get(uuid=call.data.split(':')[1])
    seller = await order.seller
    customer = await order.customer
    customer.balance += (order.amount - order.commission)
    seller.frozen_balance -= order.amount
    order.state = "seller_approved_funds"
    await order.save()
    await seller.save()
    await customer.save()
    seller_text = "Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом"
    customer_text = f"Продавец подтвердил получение ваших денежных средств по заказу № {order.uuid} TON отправлены на ваш кошелек"  \
                    f"Ваш баланс: {customer.balance} TON"
    await bot.send_message(seller.telegram_id, text=seller_text)
    await bot.send_message(customer.telegram_id, text=customer_text)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'problem_seller_no_funds')
async def problem_seller_no_funds_handler(call: types.CallbackQuery):
    date = call.message.date
    if (datetime.now() - date).total_seconds() < (4 * 60):
        return await call.message.answer("Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем.")
    order = await models.Order.get(uuid=call.data.split(':')[1])
    await call.message.edit_text("Средства не поступили")
    text = "Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам."
    await call.message.answer(text)
    payment_operation = await order.payment_operation.all().first()
    payment_operation.state = "disputed"
    order.state = "problem_seller_no_funds"
    await order.save()
    await payment_operation.save()
    customer = await order.customer
    text = "Продавец сообщил, что не получил оплату от вас."  \
           "Пришлите, пожалуйста, подтверждение оплаты (чек)"  \
           "в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение."  \
           "Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен"
    await bot.send_message(chat_id=customer.telegram_id, 
                           text=text)



