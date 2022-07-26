from typing import Union
from loader import dp
from aiogram import types
from models import models
from tortoise.queryset import Q
from keyboards.inline import buy_keyboards, deals_keyboards
from handlers.sell_coin.sell_coin_handlers import SellTonState, choice_pay_acc_sell_ton_hanlder
from utils.lang import lang_currency, lang_text
from utils.utils import trim_float
from tortoise.exceptions import DoesNotExist
from handlers.start import start

@dp.message_handler(regexp="^(Мои активные заказы)$")
@dp.message_handler(regexp="^(My active deals)$")
@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "order_pagination")
async def my_deals_handler(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.Message):
        page = 1
    else:
        page = int(message.data.split(':')[1])
        await message.message.delete()
        message = message.message
    try:
        user = await models.User.get(telegram_id=message.chat.id)
    except DoesNotExist:
        return await start(message)
    query_filter = Q(seller=user)
    query_exclude = Q(state="done") | Q(state="cancelled_by_seller") | Q(state="cancelled_by_customer")
    orders = models.Order.filter(query_filter).exclude(query_exclude)
    limit = 5
    offset = (page - 1) * limit
    count_deals = await orders.count()
    last_page = count_deals/limit
    if count_deals % limit == 0:
        last_page = int(last_page)
    elif count_deals % limit != 0:
        last_page = int(last_page + 1)
    orders = await orders.offset(offset).limit(limit).order_by("-created_at")
    if count_deals == 0:
        text = await lang_text(lang_uuid="8b158613-f1dc-4aa0-bbf0-3a4cbfce692c",        # text = "Нет активных заказов" 
                               user=user)
        keyboard = None
    else:
        text = await lang_text(lang_uuid="f11ebe57-866f-4bd3-8550-690fa288dd9f",        # text = "Выберите заказ:" 
                               user=user)
        keyboard = await deals_keyboards.show_deals_keyboard(orders=orders, 
                                                             page=page, 
                                                             last_page=last_page,
                                                             user=user)
    await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "view_order")
async def view_order_handler(call: types.CallbackQuery):
    '''Информация о заказе'''
    order = await models.Order.get(uuid=call.data.split(':')[1])
    user = await models.User.get(telegram_id=call.message.chat.id)
    if order.state == 'created':
        keyboard = await deals_keyboards.created_order_keyboard(order_uuid=order.uuid, 
                                                                user=user)
    elif order.state == 'ready_for_sale':
        keyboard = await deals_keyboards.cancel_order_keyboard(order_uuid=order.uuid, 
                                                               user=user)
    elif order.state == "wait_buyer_send_funds" or order.state == "buyer_sent_funds":
         keyboard = await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid, 
                                                            user=user)
    elif order.state == "problem_seller_no_funds" or order.state == "need_admin_resolution":
        keyboard = await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid, 
                                                           no_funds_button=False,
                                                           user=user)
    user_currency = await order.currency
    cur_name = await lang_currency(currency=user_currency,
                                   user=user)
    ton_cur = await models.Currency.get(name='TON')
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    allowed_sum_coin = order.amount-order.commission
    min_buy_sum = order.min_buy_sum if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate) else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    
    if order.parent:
        parent_order = await order.parent
        orders_payments_type = [await i.account for i in await parent_order.order_user_payment_account.all()]
    else:
        orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
    
    text = await lang_text(lang_uuid="fbddd2d5-a3cd-4a70-95a3-e0128da7c9b7",
                           user=user,
                           format={
                                    "price_one_coin":"%.5f" % price_one_coin,
                                    "currency":cur_name,
                                    "allowed_sum_coin":allowed_sum_coin,
                                    "min_buy_sum": trim_float(min_buy_sum),
                                    "full_price": trim_float(price_one_coin * allowed_sum_coin),
                                    "allowed_pay_type":', '.join([(await i.type).name for i in orders_payments_type])        
                           })
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
        edit_text = await lang_text(lang_uuid="bd7b7e0d-2420-4914-87cd-7462d9b07697",
                                    user=user)
        return await call.message.edit_text(edit_text)
    order.state = "cancelled_by_seller"
    user.balance += order.amount
    user.frozen_balance -= order.amount
    await order.save()
    await user.save()
    text = await lang_text(lang_uuid="56a300c4-ee27-4619-8112-c98c10bfdaec",
                           user=user,
                           format={
                                    "order_uuid":order.serial_int, 
                                    "order_amount":order.amount        
                           })
    # text = f"Ваш заказ № {order.uuid} отменен!\n"  \
    #        f"Мы вернули вам {order.amount} TON ваш кошелек\n"  \
    #         "Будем ждать вас снова!\n"
    await call.message.edit_text("Отменить заказ")
    await call.message.answer(text)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "add_pay_acc_in_created")
async def add_pay_acc_in_created_handler(call: types.CallbackQuery):
    '''Добавить платежки в заказ со state=created'''
    await call.message.edit_text("Внести средства")
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.state != "created":
        user = await models.User.get(telegram_id=call.message.chat.id)
        edit_text = await lang_text(lang_uuid="53d85fb5-bcf9-4ff0-ad98-3326bc02c3e7",
                                    user=user)
        return await call.message.edit_text(edit_text)
    currency = await order.currency
    await SellTonState.pay_acc_data.set()
    state = dp.get_current().current_state()
    await state.update_data(curreny_name=currency.name, order_uuid=order.uuid)
    return await choice_pay_acc_sell_ton_hanlder(call.message, state)