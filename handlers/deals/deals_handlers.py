from locale import currency
from loader import dp, bot
from aiogram import types
from models import models
from tortoise.queryset import Q
from keyboards.inline import buy_keyboards, deals_keyboards
from handlers.sell_coin.sell_coin_handlers import SellTonState, choice_pay_acc_sell_ton_hanlder

@dp.message_handler(regexp="^(Мои активные заказы)$")
async def my_deals_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    orders = await models.Order.filter(Q(seller=user)).exclude(Q(state="done") | Q(state="cancelled_by_seller") | Q(state="cancelled_by_customer")).order_by("-created_at")
    text = await models.Lang.get(uuid="8a3b4a74-d28a-4ac6-97f0-a783ee4e409a")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Выберите заказ:"
    await message.answer(text=text, reply_markup=await deals_keyboards.show_deals_keyboard(orders=orders))


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "view_order")
async def view_order_handler(call: types.CallbackQuery):
    order = await models.Order.get(uuid=call.data.split(':')[1])
    user = await models.User.get(telegram_id=call.message.chat.id)
    if order.state == 'created':
        keyboard = await deals_keyboards.created_order_keyboard(order.uuid)
    elif order.state == 'ready_for_sale':
        keyboard = await deals_keyboards.cancel_order_keyboard(order.uuid)
    elif order.state == "wait_buyer_send_funds" or order.state == "buyer_sent_funds":
         keyboard = await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid)
    elif order.state == "problem_seller_no_funds" or order.state == "need_admin_resolution":
        keyboard = await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid, no_funds_button=False)

    user_currency = await order.currency

    cur_name = user_currency.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=user_currency.uuid)
    if lang_cur:
        cur_name = lang_cur.rus

    ton_cur = await models.Currency.get(name='TON')
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    allowed_sum_coin = order.amount-order.commission
    min_buy_sum = order.min_buy_sum if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate) else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
    text = await models.Lang.get(uuid="37c86a60-28c0-4f18-8748-925817efdd2e")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(price_one_coin="%.5f" % price_one_coin,
                       currency=cur_name,
                       allowed_sum_coin=allowed_sum_coin,
                       min_buy_sum= '%.2f' % min_buy_sum,
                       full_price='%.2f' % (price_one_coin * allowed_sum_coin),
                       allowed_pay_type=', '.join([(await i.type).name for i in orders_payments_type]))
    # text = f"Цена 1 монеты {price_one_coin}\n"  \
    #         f"Общее количество монет, доступное к покупке - {allowed_sum_coin}\n"  \
    #         f"Минимальная сумма, на которую доступна покупка - {'%.2f' % min_buy_sum}\n"  \
    #         f"Общая стоимость - {'%.2f' % (price_one_coin * allowed_sum_coin)}\n"  \
    #         f"Доступные способы оплаты - {', '.join([(await i.type).name for i in orders_payments_type])}\n"
    await call.message.answer(text=text, reply_markup=keyboard)


    # cancel_order

@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "cancel_order")
async def cancel_order_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    order.state = "cancelled_by_seller"
    user.balance += order.amount
    user.frozen_balance -= order.amount
    await order.save()
    await user.save()
    text = await models.Lang.get(uuid="1c9ca33d-5d90-46c9-b506-fc7fd25a82fa")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(order_uuid=order.uuid, order_amount=order.amount)
    # text = f"Ваш заказ № {order.uuid} отменен!\n"  \
    #        f"Мы вернули вам {order.amount} TON ваш кошелек\n"  \
    #         "Будем ждать вас снова!\n"
    await call.message.edit_text("Отменить заказ")
    await call.message.answer(text)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "add_pay_acc_in_created")
async def add_pay_acc_in_created_handler(call: types.CallbackQuery):
    await call.message.edit_text("Внести средства")
    user = await models.User.get(telegram_id=call.message.chat.id)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    currency = await order.currency
    await SellTonState.pay_acc_data.set()
    state = dp.get_current().current_state()
    await state.update_data(curreny_name=currency.name, order_uuid=order.uuid)
    return await choice_pay_acc_sell_ton_hanlder(call.message, state)     

