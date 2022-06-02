from loader import dp, bot
from aiogram import types
from models import models
from tortoise.queryset import Q
from keyboards.inline import buy_keyboards, deals_keyboards

@dp.message_handler(regexp="^(Мои активные заказы)$")
async def my_deals_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    orders = await models.Order.filter(Q(seller=user)).exclude(Q(state="done") | Q(state="cancelled_by_seller") | Q(state="cancelled_by_customer")).order_by("-created_at")
    text = "Выберите заказ:"
    await message.answer(text=text, reply_markup=await deals_keyboards.show_deals_keyboard(orders=orders))


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "view_order")
async def view_order_handler(call: types.CallbackQuery):
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state == 'ready_for_sale':
        keyboard = await deals_keyboards.cancel_order_keyboard(order.uuid)
    elif order.state == "wait_buyer_send_funds" or order.state == "buyer_sent_funds":
         keyboard = await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid)
    elif order.state == "problem_seller_no_funds" or order.state == "need_admin_resolution":
        keyboard = await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid, no_funds_button=False)

    user_currency = await order.currency
    ton_cur = await models.Currency.get(name='TON')
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    allowed_sum_coin = order.amount-order.commission
    min_buy_sum = order.min_buy_sum if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate) else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
    text = f"Цена 1 монеты {price_one_coin}\n"  \
            f"Общее количество монет, доступное к покупке - {allowed_sum_coin}\n"  \
            f"Минимальная сумма, на которую доступна покупка - {'%.2f' % min_buy_sum}\n"  \
            f"Общая стоимость - {'%.2f' % (price_one_coin * allowed_sum_coin)}\n"  \
            f"Доступные способы оплаты - {', '.join([(await i.type).name for i in orders_payments_type])}\n"
    await call.message.answer(text=text, reply_markup=keyboard)


    # cancel_order

@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "cancel_order")
async def cancel_order_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    order.state = "request_cancelled_by_seller"
    user.balance += order.amount
    user.frozen_balance -= order.amount
    await order.save()
    await user.save()
    text = f"Ваш заказ № {order.uuid} отменен!\n"  \
           f"Мы вернули вам {order.amount} TON ваш кошелек\n"  \
            "Будем ждать вас снова!\n"
    await call.message.edit_text("Отменить заказ")
    await call.message.answer(text)


    