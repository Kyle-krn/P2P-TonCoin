from typing import Union
import aiogram
from keyboards.inline.keyboards import stop_state_keyboard
from loader import dp, bot
from aiogram import types
from keyboards.inline import buy_keyboards
from models import models
from tortoise.queryset import Q
from aiogram.dispatcher import FSMContext
from .state import BuyState
from .utils import check_unfinished_deal
from utils.lang import lang_currency, lang_payment_type

@dp.message_handler(regexp="^(Купить Ton)$")
@dp.callback_query_handler(lambda call: call.data == 'back_choice_currency_buy_coin')
async def buy_coin_hanlder(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        '''Кнопка назад с выбора типа оплаты'''
        message = message.message
        await message.edit_text("Назад")
    user = await models.User.get(telegram_id=message.chat.id)

    unfinished_deal, keyboard = await check_unfinished_deal(user) # Проверяем есть ли у юзера незаконченные сделки
    if unfinished_deal is True:
        return await message.answer(text="Вы имеете не завершенную сделку.", reply_markup=keyboard)

    text = await models.Lang.get(uuid="3a47043e-ce4b-4a0e-a83b-53143f5dda55")
    text = text.rus if user.lang == 'ru' else text.eng
    # text = "Выберите валюту, в которой вы хотите купить Toncoin:"
    keyboard = await buy_keyboards.currency_keyboard(user=user)
    await message.answer(text=text, reply_markup=keyboard)

    
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_currency_buy_coin')
async def choice_currency_buy_coin_handler(call: types.CallbackQuery):
    '''Покупатель выбирал валюту'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    currency_uuid = call.data.split(':')[1]
    currency = await models.Currency.get(uuid=currency_uuid)
    cur_name = await lang_currency(currency)    
    await call.message.edit_text(f"Вы выбрали: {cur_name}")
    text = await models.Lang.get(uuid="c8bc4326-82af-406d-8787-b2a461bd6a66")
    text = text.rus if user.lang == 'ru' else text.eng
    # text = "Выберите тип способа оплаты:"
    keyboard = await buy_keyboards.payment_type_keyboard(user=user, currency_uuid=currency_uuid)
    await call.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_pay_acc_buy_coin')
async def choice_pay_acc_buy_coin_handler(call: types.CallbackQuery):
    '''Покупатель выбрал тип платежки и ему отдалось список актвиных заказов'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    payment_type_uuid = call.data.split(':')[1]
    payment_type = await models.UserPaymentAccountType.get(uuid=payment_type_uuid)
    payment_type_lang = await lang_payment_type(payment_type)
    await call.message.edit_text(text=f"Вы выбрали: {payment_type_lang}")
    user_currency = await payment_type.currency
    cur_name = await lang_currency(user_currency)    
    query = Q(state="ready_for_sale") & Q(order_user_payment_account__account__type__uuid = payment_type_uuid)
    orders_list = await models.Order.filter(query).order_by('margin', 'created_at')
    ton_cur = await models.Currency.get(name='TON')
    for order in orders_list:
        price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
        allowed_sum_coin = order.amount-order.commission
        min_buy_sum = order.min_buy_sum   \
                   if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate)   \
                   else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
        orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
        text = await models.Lang.get(uuid="ddd66c21-b642-4e39-aebf-57dd80b69eb5")
        text = text.rus if user.lang == 'ru' else text.eng
        text = text.format(price_one_coin=price_one_coin,
                           currency=cur_name,
                           allowed_sum_coin=allowed_sum_coin,
                           min_buy_sum= '%.2f' % min_buy_sum,
                           full_price='%.2f' % (price_one_coin * allowed_sum_coin),
                           allowed_pay_type=', '.join([(await i.type).name for i in orders_payments_type]))
        # text = f"Цена 1 монеты {price_one_coin}\n"  \
        #        f"Общее количество монет, доступное к покупке - {allowed_sum_coin}\n"  \
        #        f"Минимальная сумма, на которую доступна покупка - {'%.2f' % min_buy_sum}\n"  \
        #        f"Общая стоимость - {'%.2f' % (price_one_coin * allowed_sum_coin)}\n"  \
        #        f"Доступные способы оплаты - {', '.join([(await i.type).name for i in orders_payments_type])}\n"
        await call.message.answer(text=text, reply_markup=await buy_keyboards.choice_order_keboard(pay_type_serial_int=payment_type.serial_int, 
                                                                                                   order_uuid=order.uuid))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'buy_order')
async def buy_order_hanlder(call: types.CallbackQuery):
    '''Покупатель выбрал заказ'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    pay_type_serial_int = call.data.split(':')[1]
    pay_type = await models.UserPaymentAccountType.get(serial_int=pay_type_serial_int)
    order_uuid = call.data.split(':')[2]
    order = await models.Order.get(uuid=order_uuid)
    if order.state != "ready_for_sale":
        return await call.message.answer(text="Данный заказ к сожалению сейчас не доступен.")

    unfinished_deal, keyboard = await check_unfinished_deal(user)
    if unfinished_deal is True:
        return await call.message.answer(text="Вы имеете не завершенную сделку.", reply_markup=keyboard)

    ton_cur = await models.Currency.get(name='TON')
    user_currency = await order.currency

    cur_name = await lang_currency(user_currency)    
    min_buy_sum = order.min_buy_sum \
               if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate)  \
             else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    text = await models.Lang.get(uuid="e4ae3df2-f1ce-4003-86c0-36d1fc7028b6")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(min_buy_sum=min_buy_sum,
                       full_price="%.2f" % (price_one_coin * (order.amount-order.commission)),
                       currency=cur_name)
    # text = f"Введите количество Toncoin, которое вы хотите купить"  \
    #        f"(сумма покупки должна быть не меньше {min_buy_sum})"
    await BuyState.buy_amount.set()
    
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
    '''Покупатель ввел кол-во валюты на которую он хочет купить TON'''
    user_data = await state.get_data()
    user = await models.User.get(telegram_id=message.chat.id)
    order = await models.Order.get(uuid=user_data['order_uuid'])
    try:
        await user_data['message'].edit_reply_markup(None)
    except aiogram.utils.exceptions.MessageNotModified:
        pass

    try:
        buy_amount = float(message.text)
        if (user_data['min_buy_sum'] <= buy_amount < (user_data['price_one_coin'] * (order.amount-order.commission))) is False:
            raise ValueError
    except (ValueError, TypeError):

        user_currency = await order.currency

        cur_name = await lang_currency(user_currency) 

        text = await models.Lang.get(uuid="efeb95c8-46b0-485e-bd44-d27a4b0d633d")
        text = text.rus if user.lang == 'ru' else text.eng
        text = text.format(min_buy_sum=user_data['min_buy_sum'],
                           full_price="%.2f" % (user_data['price_one_coin'] * (order.amount-order.commission)),
                           currency=cur_name)
        # text = f"Введите количество Toncoin, которое вы хотите купить"  \
        #    f"(сумма покупки должна быть не меньше {user_data['min_buy_sum']})"
        msg = await message.answer(text)
        return await state.update_data(message=msg)
        
    buy_ton_amount = buy_amount / user_data['price_one_coin']
    
    if order.state != "ready_for_sale":
        await state.finish()
        return await message.answer(text="Данный заказ к сожалению сейчас не доступен.")
    
    # Если у юзера есть незавершенная сделка и он выбирает еще одну сделку
    unfinished_deal, keyboard = await check_unfinished_deal(user)
    if unfinished_deal is True:
        return await message.answer(text="Вы имеете не завершенную сделку.", reply_markup=keyboard)
    
    pay_type = await models.UserPaymentAccountType.get(uuid=user_data["pay_type_uuid"])
    if ((order.amount - order.commission) - buy_ton_amount) > 0.01:
        new_order = await models.Order.create(state="wait_buyer_send_funds", 
                                              parent=order,
                                              customer=user,
                                              amount=buy_ton_amount,
                                              final_price=buy_amount,
                                              origin_amount=order.origin_amount,
                                              margin=order.margin,
                                              commission=buy_ton_amount * 0.01,
                                              min_buy_sum=order.min_buy_sum,
                                              currency_id=order.currency_id,
                                              seller_id=order.seller_id,
                                              customer_pay_type=pay_type)
        await models.OrderStateChange.create(order=new_order, old_state="created children order", new_state="wait_buyer_send_funds")
        old_amount = order.amount
        order.amount -= buy_ton_amount
        order.commission = order.amount * 0.01
        await order.save()
        await models.OrderAmountChange.create(order=order,
                                              target_order=new_order, 
                                              old_amount=old_amount, 
                                              new_amount=order.amount) 
        order = new_order
    else:
        await models.OrderStateChange.create(order=order, old_state=order.state, new_state="wait_buyer_send_funds")
        order.state = "wait_buyer_send_funds"
        order.customer = user
        order.final_price = buy_amount
        order.customer_pay_type = pay_type
        await order.save()
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
    user = await models.User.get(telegram_id=message.chat.id)
    if order.parent:
        parent_order = await order.parent
        pay_account = await parent_order.order_user_payment_account.filter(account__type__uuid=order.customer_pay_type_id)
    else:
        pay_account = await order.order_user_payment_account.filter(account__type__uuid=order.customer_pay_type_id)
    user_data_text = ""
    for k,v in (await pay_account[0].account).data.items():
        user_data_text += f"{k}: {v}\n"
    
    currency = await order.currency
    cur_name = await lang_currency(currency) 

    text = await models.Lang.get(uuid="854b6bd4-0147-4ee1-9293-85eefaf34f90")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(final_price=float(order.final_price),
                       currency=cur_name,
                       user_data_text=user_data_text,
                       amount=order.amount - order.commission)
    # text = "У вас 15 минут для завершение заказа.\n"  \
    #        "Этапы совершения заказа:\n"  \
    #        "вы перечисляете деньги продавцу\n"  \
    #        "мы отправляем вам TON на ваш кошелек в системе\n\n"  \
    #       f"Отправьте {float(order.final_price)}$ по следующим реквизитам:\n"  \
    #       f"{user_data_text}\n"  \
    #       f"Вы получите {order.amount - order.commission} TON\n"  \
    #        "После оплаты нажмите кнопку Я отправил средства"
    keyboard = await buy_keyboards.send_money_order(order.uuid)
    await message.answer(text=text, reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_buy_order')
async def cancel_buy_order_handler(call :types.CallbackQuery):
    '''Покупатель отменяет сделку'''
    order = await models.Order.get(uuid=call.data.split(':')[1])
    if order.parent:
        order_parent = await order.parent
        order_parent.amount += order.amount
        order_parent.commission = order_parent.amount * 0.01
        await models.OrderAmountChange.create(order=order, 
                                              target_order=order_parent, 
                                              old_amount=order.amount, 
                                              new_amount=0) 
        order.amount = 0
        order.commission = 0
        await models.OrderStateChange.create(order=order, old_state=order.state, new_state="cancelled_by_customer")
        order.state = "cancelled_by_customer"
        await order.save()
        await order_parent.save()
    else:
        await models.OrderStateChange.create(order=order, old_state=order.state, new_state="ready_for_sale")
        order.state = "ready_for_sale"
        order.customer = None
        order.final_price = None
        order.customer_pay_type = None
        await order.save()

    # text = "Заказ отменен."
    user = await models.User.get(telegram_id=call.message.chat.id)
    text = await models.Lang.get(uuid="1235401b-7b99-4798-9ea2-82f94e1f46b4")
    text = text.rus if user.lang == 'ru' else text.eng
    await call.message.edit_text(text=text)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'send_money_order')
async def send_money_order_handler(call: types.CallbackQuery):
    '''Покупатель отправил деньги'''
    order = await models.Order.get(uuid=call.data.split(":")[1])
    if order.parent:
        parent_order = await order.parent
        pay_account = await parent_order.order_user_payment_account.filter(account__type__uuid=order.customer_pay_type_id)
    else:
        pay_account = await order.order_user_payment_account.filter(account__type__uuid=order.customer_pay_type_id)
    await models.OrderStateChange.create(order=order, old_state=order.state, new_state="buyer_sent_funds")
    order.state = "buyer_sent_funds"
    await order.save()
    await models.PaymentOperation.create(order=order,
                                         sender_id=order.customer_id,
                                         recipient_id=order.seller_id,
                                         recipient_data=(await pay_account[0].account).data,
                                         state="created")
    seller = await order.seller

    currency = await order.currency
    cur_name = await lang_currency(currency)

    text_for_seller = await models.Lang.get(uuid="f1defc4d-e4cc-4afa-be24-5f911a4508bf")
    text_for_seller = text_for_seller.rus if seller.lang == 'ru' else text_for_seller.eng
    text_for_seller = text_for_seller.format(uuid=order.serial_int, 
                                             currency=cur_name,
                                             final_price=float(order.final_price))
    # text = f"По заказу №{order.uuid} покупатель отправил денежные средства в размере {float(order.final_price)}$.\n"  \
    #         "Подтвердите получение оплаты, нажав кнопку Я получил средства, либо нажмите Средства не поступили, если деньги не поступили на ваш счет"
    await call.message.edit_text("Ожидайте ответа от продавца.")
    await bot.send_message(seller.telegram_id, text=text_for_seller, reply_markup=await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid))