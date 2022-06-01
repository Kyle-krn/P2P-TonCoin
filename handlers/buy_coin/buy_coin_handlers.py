from typing import Union

import aiogram
from keyboards.inline.keyboards import stop_state_keyboard
from loader import dp
from aiogram import types
from keyboards.inline import buy_keyboards
from models import models
from tortoise.queryset import Q
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


class BuyState(StatesGroup):
    buy_amount = State()


@dp.message_handler(regexp="^(Купить Ton)$")
@dp.callback_query_handler(lambda call: call.data == 'back_choice_currency_buy_coin')
async def buy_coin_hanlder(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        message = message.message
        await message.edit_text("Назад")
    user = await models.User.get(telegram_id=message.chat.id)
    buy_order_user = await models.Order.get_or_none(customer=user, state="wait_buyer_send_funds")
    if buy_order_user:
        return await message.answer(text="Вы имеете не завершенную сделку.", reply_markup=await buy_keyboards.go_to_buy_order_keyboard(buy_order_user.uuid))
    text = "Выберите валюту, в которой вы хотите купить Toncoin:"
    keyboard = await buy_keyboards.currency_keyboard(user=user)
    await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_currency_buy_coin')
async def choice_currency_buy_coin_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    currency_uuid = call.data.split(':')[1]
    currency = await models.Currency.get(uuid=currency_uuid)
    cur_name = currency.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
    if lang_cur:
        cur_name = lang_cur.rus
    await call.message.edit_text(f"Вы выбрали: {cur_name}")
    text = "Выберите тип способа оплаты:"
    keyboard = await buy_keyboards.payment_type_keyboard(user=user, currency_uuid=currency_uuid)
    await call.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_pay_acc_buy_coin')
async def choice_pay_acc_buy_coin_handler(call: types.CallbackQuery):
    payment_type_uuid = call.data.split(':')[1]
    payment_type = await models.UserPaymentAccountType.get(uuid=payment_type_uuid)
    
    name = payment_type.name
    lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=payment_type.uuid)
    if lang_type:
        name = lang_type.rus
    await call.message.edit_text(text=f"Вы выбрали: {name}")

    user_currency = await payment_type.currency
    query = Q(state="ready_for_sale") & Q(order_user_payment_account__account__type__uuid = payment_type_uuid)
    orders_list = await models.Order.filter(query).order_by('margin', 'created_at')
    ton_cur = await models.Currency.get(name='TON')
    for order in orders_list:
        price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
        allowed_sum_coin = order.amount-order.commission
        min_buy_sum = order.min_buy_sum if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate) else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
        orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
        text = f"Цена 1 монеты {price_one_coin}\n"  \
               f"Общее количество монет, доступное к покупке - {allowed_sum_coin}\n"  \
               f"Минимальная сумма, на которую доступна покупка - {'%.2f' % min_buy_sum}\n"  \
               f"Общая стоимость - {'%.2f' % (price_one_coin * allowed_sum_coin)}\n"  \
               f"Доступные способы оплаты - {', '.join([(await i.type).name for i in orders_payments_type])}\n"
        await call.message.answer(text=text, reply_markup=await buy_keyboards.choice_order_keboard(pay_type_serial_int=payment_type.serial_int, 
                                                                                                   order_uuid=order.uuid))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'buy_order')
async def buy_order_hanlder(call: types.CallbackQuery):
    pay_type_serial_int = call.data.split(':')[1]
    pay_type = await models.UserPaymentAccountType.get(serial_int=pay_type_serial_int)
    order_uuid = call.data.split(':')[2]
    order = await models.Order.get(uuid=order_uuid)
    if order.state != "ready_for_sale":
        return await call.message.answer(text="Данный заказ к сожалентю сейчас не доступен.")
    ton_cur = await models.Currency.get(name='TON')
    user_currency = await order.currency
    min_buy_sum = order.min_buy_sum if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate) else  \
                  (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    text = f"Введите количество Toncoin, которое вы хотите купить"  \
           f"(сумма покупки должна быть не меньше {min_buy_sum})"
    await BuyState.buy_amount.set()
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    state = dp.get_current().current_state()
    msg = await call.message.answer(text=text, reply_markup=await stop_state_keyboard())
    await state.update_data(min_buy_sum=min_buy_sum,
                            ton_cur=ton_cur.exchange_rate, 
                            user_cur=user_currency.exchange_rate, 
                            price_one_coin=price_one_coin,
                            order_uuid=order.uuid,
                            pay_type_uuid=pay_type.uuid,
                            max_buy_sum=price_one_coin * (order.amount-order.commission),
                            message=msg)
    


@dp.message_handler(state=BuyState.buy_amount, content_types=['text'])
async def buy_amount_state(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        await user_data['message'].edit_reply_markup(None)
    except aiogram.utils.exceptions.MessageNotModified:
        pass

    try:
        buy_amount = float(message.text)
        if (user_data['min_buy_sum'] < buy_amount < user_data['max_buy_sum']) is False:
            raise ValueError
    except (ValueError, TypeError):
        text = f"Введите количество Toncoin, которое вы хотите купить"  \
           f"(сумма покупки должна быть не меньше {user_data['min_buy_sum']})"
        msg = await message.answer(text)
        return await state.update_data(message=msg)
        
    buy_ton_amount = buy_amount / user_data['price_one_coin']
    order = await models.Order.get(uuid=user_data['order_uuid'])
    user = await models.User.get(telegram_id=message.chat.id)
    pay_type = await models.UserPaymentAccountType.get(uuid=user_data["pay_type_uuid"])
    if ((order.amount - order.commission) - buy_ton_amount) > 0.01:
        new_order = await models.Order.create(state="wait_buyer_send_funds", 
                                              parent=order,
                                              customer=user,
                                              amount=buy_ton_amount,
                                              final_price=buy_amount,
                                              origin_amount=order.origin_amount,
                                              margin=order.margin,
                                              commission=order.commission,
                                              min_buy_sum=order.min_buy_sum,
                                              currency_id=order.currency_id,
                                              seller_id=order.seller_id,
                                              customer_pay_type=pay_type)
        old_amount = order.amount
        order.amount -= buy_ton_amount
        await order.save()
        await models.OrderAmountChange.create(order=order,
                                              target_order=new_order, 
                                              old_amount=old_amount, 
                                              new_amount=order.amount) 
        order = new_order
    else:
        order.state = ""

    await state.finish()
    return await view_buy_order_handler(message, order)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'go_to_order')
async def view_buy_order_handler(message: Union[types.Message, types.CallbackQuery], 
                                 order: models.Order = None,
                                 ):
    if order is None:
        order = await models.Order.get(uuid=message.data.split(':')[1])
        message = message.message
        await message.edit_text("Перейти к сделке")
    if order.parent:
        parent_order = await order.parent
        pay_account = await parent_order.order_user_payment_account.filter(account__type__uuid=order.customer_pay_type_id)
    else:
        pay_account = await order.order_user_payment_account.filter(account__type__uuid=order.customer_pay_type_id)
    
    user_data_text = ""
    for k,v in (await pay_account[0].account).data.items():
        user_data_text += f"{k}: {v}\n"
    text = "У вас 15 минут для завершение заказа.\n"  \
           "Этапы совершения заказа:\n"  \
           "вы перечисляете деньги продавцу\n"  \
           "мы отправляем вам TON на ваш кошелек в системе\n\n"  \
          f"Отправьте {float(order.final_price)}$ по следующим реквизитам:\n"  \
          f"{user_data_text}"  \
           "После оплаты нажмите кнопку Я отправил средства"
    keyboard = await buy_keyboards.send_money_order(order.uuid)
    await message.answer(text=text, reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_buy_order')
async def cancel_buy_order_handler(call :types.CallbackQuery):
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.parent:
        order_parent = await order.parent
        order_parent.amount += order.amount
        await models.OrderAmountChange.create(order=order, 
                                              target_order=order_parent, 
                                              old_amount=order.amount, 
                                              new_amount=0) 
        order.amount = 0
        order.state = "cancelled_by_customer"
        await order.save()
        await order_parent.save()
    text = "Заказ отменен."
    await call.message.edit_text(text=text)
