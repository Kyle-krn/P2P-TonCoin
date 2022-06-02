from loader import dp, bot
from aiogram import types
from models import models

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
