from loader import dp
from aiogram import types
from models import models
from tortoise.queryset import Q
from keyboards.inline import buy_keyboards, deals_keyboards
from handlers.sell_coin.sell_coin_handlers import SellTonState, choice_pay_acc_sell_ton_hanlder
from utils.lang import lang_currency


@dp.message_handler(regexp="^(Мои активные заказы)$")
async def my_deals_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    orders = await models.Order.filter(Q(seller=user)).exclude(Q(state="done") | Q(state="cancelled_by_seller") | Q(state="cancelled_by_customer")).order_by("-created_at")
    text = await models.Lang.get(uuid="f11ebe57-866f-4bd3-8550-690fa288dd9f")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Выберите заказ:"
    await message.answer(text=text, reply_markup=await deals_keyboards.show_deals_keyboard(orders=orders))


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "view_order")
async def view_order_handler(call: types.CallbackQuery):
    '''Информация о заказе'''
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

    cur_name = await lang_currency(user_currency)
    
    ton_cur = await models.Currency.get(name='TON')
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    allowed_sum_coin = order.amount-order.commission
    min_buy_sum = order.min_buy_sum if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate) else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    
    if order.parent:
        parent_order = await order.parent
        orders_payments_type = [await i.account for i in await parent_order.order_user_payment_account.all()]
    else:
        orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
    
    text = await models.Lang.get(uuid="fbddd2d5-a3cd-4a70-95a3-e0128da7c9b7")
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


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "cancel_order")
async def cancel_order_handler(call: types.CallbackQuery):
    '''Отмена заказа'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state not in ("created", "ready_for_sale"):
        return await call.message.edit_text("Нельзя отменить заказ.")
    order.state = "cancelled_by_seller"
    user.balance += order.amount
    user.frozen_balance -= order.amount
    await order.save()
    await user.save()
    text = await models.Lang.get(uuid="56a300c4-ee27-4619-8112-c98c10bfdaec")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(order_uuid=order.serial_int + 5432, 
                       order_amount=order.amount)
    # text = f"Ваш заказ № {order.uuid} отменен!\n"  \
    #        f"Мы вернули вам {order.amount} TON ваш кошелек\n"  \
    #         "Будем ждать вас снова!\n"
    await call.message.edit_text("Отменить заказ")
    await call.message.answer(text)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "add_pay_acc_in_created")
async def add_pay_acc_in_created_handler(call: types.CallbackQuery):
    '''Добавить платежки в заказ со state=created'''
    await call.message.edit_text("Внести средства")
    user = await models.User.get(telegram_id=call.message.chat.id)
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state != "created":
        return await call.message.edit_text("Нельзя добавить платежные аккаунты в этот заказ.")
    currency = await order.currency
    await SellTonState.pay_acc_data.set()
    state = dp.get_current().current_state()
    await state.update_data(curreny_name=currency.name, order_uuid=order.uuid)
    return await choice_pay_acc_sell_ton_hanlder(call.message, state)     

