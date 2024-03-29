from typing import Union
from uuid import UUID
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
from utils.lang import lang_currency, lang_payment_type, lang_text
from utils.utils import trim_float
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from tortoise.exceptions import DoesNotExist
from handlers.start import start
@dp.message_handler(regexp="^(Купить Ton)$")
@dp.message_handler(regexp="^(Buy Ton)$")
@dp.callback_query_handler(lambda call: call.data == 'back_choice_currency_buy_coin')
async def buy_coin_hanlder(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        '''Кнопка назад с выбора типа оплаты'''
        message = message.message
        user = await models.User.get(telegram_id=message.chat.id)    
        edit_text = await lang_text(lang_uuid="eef933b0-e3bc-46ed-8461-8226fd5f090f",
                                    user=user)
        await message.edit_text(edit_text)
    else:
        try:
            user = await models.User.get(telegram_id=message.chat.id)
        except DoesNotExist:
            return await start(message)
    unfinished_deal, keyboard = await check_unfinished_deal(user) # Проверяем есть ли у юзера незаконченные сделки
    if unfinished_deal is True:
        return await message.answer(text="Вы имеете не завершенную сделку.", reply_markup=keyboard)

    text = await lang_text(lang_uuid="3a47043e-ce4b-4a0e-a83b-53143f5dda55",
                           user=user)
    
    curency_list_count = await models.Currency.filter(orders__state="ready_for_sale").exclude(orders__seller=user).count()
    if curency_list_count > 0:
        text = await lang_text(lang_uuid="3a47043e-ce4b-4a0e-a83b-53143f5dda55",        # text = "К сожалению в данный момент нет объявлений о продаже"
                               user=user)
        keyboard = await buy_keyboards.currency_keyboard(user=user)
    else:                                   
        text = await lang_text(lang_uuid="b620cad0-5c97-4752-9d44-20ff6d622b10",        # text = "Выберите валюту, в которой вы хотите купить Toncoin:"
                               user=user)
        keyboard = None
    await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_currency_buy_coin')
async def choice_currency_buy_coin_handler(call: types.CallbackQuery):
    '''Покупатель выбирал валюту'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    currency_uuid = call.data.split(':')[1]
    currency = await models.Currency.get(uuid=currency_uuid)
    cur_name = await lang_currency(currency=currency,
                                   user=user)  
    edit_text = await lang_text(lang_uuid="93a3e2ea-a462-462a-8fca-a3689d3d0690",
                                user=user,
                                format={
                                    "cur_name": cur_name
                                })
    await call.message.edit_text(edit_text)

    text = await lang_text(lang_uuid="c8bc4326-82af-406d-8787-b2a461bd6a66",
                           user=user)
    # text = "Выберите тип способа оплаты:"
    keyboard = await buy_keyboards.payment_type_keyboard(user=user, currency_uuid=currency_uuid)
    await call.message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_pay_acc_buy_coin')
async def choice_pay_acc_buy_coin_handler(call: types.CallbackQuery):
    '''Покупатель выбрал тип платежки и ему отдалось список актвиных заказов'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    payment_type_uuid = call.data.split(':')[1]
    payment_type = await models.UserPaymentAccountType.get(uuid=payment_type_uuid)
    payment_type_lang = await lang_payment_type(payment_type=payment_type,
                                                user=user)
    edit_text = await lang_text(lang_uuid="93a3e2ea-a462-462a-8fca-a3689d3d0690",
                                user=user,
                                format={
                                    "cur_name": payment_type_lang
                                })
    await call.message.edit_text(text=edit_text)
    user_currency = await payment_type.currency
    cur_name = await lang_currency(currency=user_currency,
                                   user=user)
    query = Q(state="ready_for_sale") & Q(order_user_payment_account__account__type__uuid=payment_type_uuid)
    orders_list = await models.Order.filter(query).order_by('margin', 'created_at')
    ton_cur = await models.Currency.get(name='TON')
    for order in orders_list:
        price_one_coin = (float(user_currency.exchange_rate)  \
                        * float(ton_cur.exchange_rate))   \
                        * (1+(order.margin/100))
        allowed_sum_coin = order.amount-order.commission
        min_buy_sum = order.min_buy_sum   \
                   if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate)   \
                   else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
        orders_payments_type = [await i.account for i in await order.order_user_payment_account.all()]
        text = await lang_text(lang_uuid="fbddd2d5-a3cd-4a70-95a3-e0128da7c9b7",
                               user=user,
                               format={
                                        "price_one_coin": trim_float(price_one_coin),
                                        "currency":cur_name,
                                        "allowed_sum_coin":allowed_sum_coin,
                                        "min_buy_sum": trim_float(min_buy_sum),
                                        "full_price":trim_float(price_one_coin * allowed_sum_coin),
                                        "allowed_pay_type":', '.join([(await i.type).name for i in orders_payments_type])
                               })
        # text = f"Цена 1 монеты {price_one_coin}\n"  \
        #        f"Общее количество монет, доступное к покупке - {allowed_sum_coin}\n"  \
        #        f"Минимальная сумма, на которую доступна покупка - {'%.2f' % min_buy_sum}\n"  \
        #        f"Общая стоимость - {'%.2f' % (price_one_coin * allowed_sum_coin)}\n"  \
        #        f"Доступные способы оплаты - {', '.join([(await i.type).name for i in orders_payments_type])}\n"
        await call.message.answer(text=text, reply_markup=await buy_keyboards.choice_order_keboard(pay_type_serial_int=payment_type.serial_int, 
                                                                                                   order_uuid=order.uuid,
                                                                                                   user=user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'buy_order')
async def buy_order_hanlder(call: types.CallbackQuery):
    '''Покупатель выбрал заказ'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    pay_type_serial_int = call.data.split(':')[1]
    pay_type = await models.UserPaymentAccountType.get(serial_int=pay_type_serial_int)
    order_uuid = call.data.split(':')[2]
    order = await models.Order.get(uuid=order_uuid)
    if order.state != "ready_for_sale":
        text = await lang_text(lang_uuid="591918f9-63db-4a54-8912-458368c29113",
                               user=user)
        return await call.message.answer(text=text)

    unfinished_deal, keyboard = await check_unfinished_deal(user)
    if unfinished_deal is True:
        text = await lang_text(lang_uuid="9afbc187-ca12-4ff6-8f65-67b49c66b222",
                               user=user)
        return await call.message.answer(text=text, 
                                         reply_markup=keyboard)

    ton_cur = await models.Currency.get(name='TON')
    user_currency = await order.currency

    cur_name = await lang_currency(currency=user_currency,
                                   user=user)    
    min_buy_sum = order.min_buy_sum \
               if order.min_buy_sum < (order.amount - order.commission) * float(ton_cur.exchange_rate)* float(user_currency.exchange_rate)  \
             else (order.amount - order.commission) * float(ton_cur.exchange_rate) * float(user_currency.exchange_rate)
    price_one_coin = (float(user_currency.exchange_rate) * float(ton_cur.exchange_rate)) * (1+(order.margin/100))
    
    text = await lang_text(lang_uuid="efeb95c8-46b0-485e-bd44-d27a4b0d633d",
                           user=user,
                           format={
                                "min_buy_sum":trim_float(min_buy_sum),
                                "full_price":trim_float(price_one_coin * (order.amount-order.commission)),
                                "currency":cur_name        
                           })
    # text = f"Введите количество Toncoin, которое вы хотите купить"  \
    #        f"(сумма покупки должна быть не меньше {min_buy_sum})"
    await BuyState.buy_amount.set()
    state = dp.get_current().current_state()
    msg = await call.message.answer(text=text, reply_markup=await stop_state_keyboard(user))
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
        message.text = message.text.replace(",", ".")
        buy_amount = float(message.text)
        if (user_data['min_buy_sum'] <= buy_amount <= (user_data['price_one_coin'] * (order.amount-order.commission))) is False:
            raise ValueError
    except (ValueError, TypeError):

        user_currency = await order.currency

        cur_name = await lang_currency(currency=user_currency,
                                       user=user) 

        text = await lang_text(lang_uuid="efeb95c8-46b0-485e-bd44-d27a4b0d633d",
                               user=user,
                               format={
                                   "min_buy_sum": trim_float(user_data['min_buy_sum']),
                                   "full_price": trim_float(user_data['price_one_coin'] * (order.amount-order.commission)),
                                   "currency":cur_name
                               })
        # text = f"Введите количество Toncoin, которое вы хотите купить"  \
        #    f"(сумма покупки должна быть не меньше {user_data['min_buy_sum']})"
        msg = await message.answer(text)
        return await state.update_data(message=msg)
        
    buy_ton_amount = buy_amount / user_data['price_one_coin']
    
    if order.state != "ready_for_sale":
        await state.finish()
        text = await lang_text(lang_uuid="591918f9-63db-4a54-8912-458368c29113",
                               user=user)
        return await message.answer(text=text)
    
    # Если у юзера есть незавершенная сделка и он выбирает еще одну сделку
    unfinished_deal, keyboard = await check_unfinished_deal(user)
    if unfinished_deal is True:
        text = await lang_text(lang_uuid="9afbc187-ca12-4ff6-8f65-67b49c66b222",
                               user=user)
        return await message.answer(text=text, reply_markup=keyboard)
    
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
        
        await models.OrderStateChange.create(order=new_order, 
                                             old_state="created children order", 
                                             new_state="wait_buyer_send_funds")
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
        await models.OrderStateChange.create(order=order, 
                                             old_state=order.state, 
                                             new_state="wait_buyer_send_funds")
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
        user = await models.User.get(telegram_id=message.chat.id)
        edit_text = await lang_text(lang_uuid="4ed8b02d-8577-42f3-8a85-67939b608fc6",
                                    user=user)
        await message.edit_text(edit_text)
    else:
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
    cur_name = await lang_currency(currency=currency,
                                   user=user) 
    text = await lang_text(lang_uuid="854b6bd4-0147-4ee1-9293-85eefaf34f90",
                           user=user,
                           format={
                                    "final_price":float(order.final_price),
                                    "currency":cur_name,
                                    "user_data_text":user_data_text,
                                    "amount":order.amount - order.commission        
                           })
    # text = "У вас 15 минут для завершение заказа.\n"  \
    #        "Этапы совершения заказа:\n"  \
    #        "вы перечисляете деньги продавцу\n"  \
    #        "мы отправляем вам TON на ваш кошелек в системе\n\n"  \
    #       f"Отправьте {float(order.final_price)}$ по следующим реквизитам:\n"  \
    #       f"{user_data_text}\n"  \
    #       f"Вы получите {order.amount - order.commission} TON\n"  \
    #        "После оплаты нажмите кнопку Я отправил средства"
    keyboard = await buy_keyboards.send_money_order(order_uuid=order.uuid,
                                                    user=user)
    await message.answer(text=text, reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_buy_order')
async def cancel_buy_order_handler(call :types.CallbackQuery = None, 
                                   order_uuid: UUID = None):
    '''Покупатель отменяет сделку'''
    order_uuid = call.data.split(':')[1] if call else order_uuid
    order = await models.Order.get(uuid=order_uuid)
    if order.state != "wait_buyer_send_funds" or order.state != "problem_seller_no_funds":
        return
    customer = await order.customer
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
    if call:
        user = await models.User.get(telegram_id=call.message.chat.id)
        text = await lang_text(lang_uuid="1235401b-7b99-4798-9ea2-82f94e1f46b4",
                            user=user)
        return await call.message.edit_text(text=text)
    else:
        # 
        text = await lang_text(lang_uuid="0098f880-d6cc-472b-ad64-6454fb18f689",
                            user=customer,
                            format={"order_id": order.serial_int})
        try:
            return await bot.send_message(chat_id=customer.telegram_id, text= text)
        except (ChatNotFound, BotBlocked):
            pass


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'send_money_order')
async def send_money_order_handler(call: types.CallbackQuery):
    '''Покупатель отправил деньги'''
    order = await models.Order.get(uuid=call.data.split(":")[1])
    if order.state != "wait_buyer_send_funds":
        return await call.message.edit_text("Этот заказ больше недоступен.")
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
    cur_name = await lang_currency(currency=currency,
                                   user=seller)
    
    order_id = order.serial_int
    if order.parent_id:
        parent_order = await order.parent
        order_id = parent_order.serial_int

    text_for_seller = await lang_text(lang_uuid="f1defc4d-e4cc-4afa-be24-5f911a4508bf",
                                      user=seller,
                                      format={
                                            "uuid":order_id, 
                                            "currency":cur_name,
                                            "final_price":float(order.final_price)
                                      })
    # text = f"По заказу №{order.uuid} покупатель отправил денежные средства в размере {float(order.final_price)}$.\n"  \
    #         "Подтвердите получение оплаты, нажав кнопку Я получил средства, либо нажмите Средства не поступили, если деньги не поступили на ваш счет"
    edit_text = await lang_text(lang_uuid="73323c38-3f22-48db-8da6-fe31fba72ef0",
                                user=await order.customer)
    await call.message.edit_text(edit_text)
    await bot.send_message(seller.telegram_id, 
                           text=text_for_seller, 
                           reply_markup=await buy_keyboards.keyboard_for_seller(order_uuid=order.uuid,
                                                                                user=seller))