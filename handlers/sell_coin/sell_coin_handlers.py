from typing import Union
from keyboards.inline.keyboards import stop_state_keyboard
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import currency_keyboards, payment_account_keyboards
from aiogram.dispatcher import FSMContext
from tortoise.queryset import Q
from utils.lang import lang_currency, lang_payment_type
from utils.validate_ton_address import get_currency_ton
from keyboards.inline import sell_keyboards
from .state import SellTonState
import aiogram


@dp.message_handler(regexp="^(Продать Ton)$")
@dp.message_handler(regexp="^(Sell Ton)$")
async def sell_ton_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    if user.balance < 0.1:
        # text = "Пополните баланс для создания заказа на продажу TonCoin"
        text = await models.Lang.get(uuid="aa66b9f2-8bf6-4d1b-9e8c-207ef6787935")
        text = text.rus if user.lang == "ru" else text.eng
        return await message.answer(text=text)
    await SellTonState.amount.set()
    state = dp.get_current().current_state()
    text = await models.Lang.get(uuid="c060e220-26d5-4138-ac3d-edda436a659a")
    text = text.rus if user.lang == "ru" else text.eng
    text = text.format(balance=user.balance)
    # text = f"Введите количество TON, которое вы хотите продать (число от 0.1 до {user.balance})"
    message = await message.answer(text, reply_markup=await stop_state_keyboard(user))
    await state.update_data(message=message)


@dp.message_handler(state=SellTonState.amount, content_types=['text'])
async def sell_ton_state(message: types.Message, state: FSMContext):
    """Продавец вводит кол-во Ton на продажу"""
    user_data = await state.get_data()
    try:
        await user_data['message'].edit_reply_markup(None)
    except aiogram.utils.exceptions.MessageNotModified:
        pass
    amount = message.text.replace(',', '.')
    user = await models.User.get(telegram_id=message.chat.id)
    try:
        amount = float(amount)
        if amount > user.balance:
            raise ValueError
    except (ValueError, TypeError):
        text = await models.Lang.get(uuid="82daaee6-9971-449e-99af-0513ccccf5cc")
        text = text.rus if user.lang == "ru" else text.eng
        text = text.format(balance=user.balance)
        # text = f"Неверный формат ввода. Введите число от 0.1 до {user.balance}"
        message = await message.answer(text, reply_markup=await stop_state_keyboard(user))
        return await state.update_data(message=message)
    text = await models.Lang.get(uuid="f32f4c20-acae-4017-9be8-daaf71db151c")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100\n"  \
    #        "Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap"
    await state.update_data(amount=amount)
    await SellTonState.next()
    message = await message.answer(text=text, reply_markup=await stop_state_keyboard(user))
    await state.update_data(message=message)


@dp.message_handler(state=SellTonState.fee, content_types=['text'])
async def fee_state(message: types.Message, state:FSMContext):
    '''Продавец вводит наценку'''
    user = await models.User.get(telegram_id=message.chat.id)
    user_data = await state.get_data()
    try:
        await user_data['message'].edit_reply_markup(None)
    except aiogram.utils.exceptions.MessageNotModified:
        pass
    fee = message.text.replace(',', '.')
    try:
        fee = float(fee)
        if (1 <= fee <= 100) is False:
            raise ValueError 
    except (ValueError, TypeError):
        text = await models.Lang.get(uuid="1879a3dd-825f-4a50-97e3-9e62d183dc8c")
        text = text.rus if user.lang == "ru" else text.eng
        # text = "Неверный формат ввода. Введите число от 1 до 100"
        message = await message.answer(text)
        return await state.update_data(message=message)
    await state.update_data(fee=fee)
    await SellTonState.next()
    text = await models.Lang.get(uuid="10efd114-3a48-4bd4-986b-ac8f5ff207b9")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Выберите валюту, в которой вы хотите продать TonCoin:"
    reply_markup = await currency_keyboards.currency_keyboard(callback="sell_coin_currency")
    message = await message.answer(text=text, reply_markup=reply_markup)
    await state.update_data(message=message)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'sell_coin_currency', state=SellTonState.currency)
async def choice_currency_state(call: types.CallbackQuery, state: FSMContext):
    '''Продавец выбирает валюту'''
    await SellTonState.next()
    user = await models.User.get(telegram_id=call.message.chat.id)
    # ton_currency = await get_currency_ton()
    ton_cur = await models.Currency.get(name='TON')
    user_data = await state.get_data()
    currency = await models.Currency.get(name=call.data.split(':')[1])
    cur_name = await lang_currency(currency)
    await user_data['message'].edit_text(text=f"Вы выбрали: {cur_name}")
    max_price = float("%.2f" % (float(user_data['amount']) * float(ton_cur.exchange_rate) * float(currency.exchange_rate)))
    await state.update_data(curreny_name=call.data.split(':')[1], max_price=max_price)
    text = await models.Lang.get(uuid="04e0b432-a089-473b-9215-562db2af04d1")
    text = text.rus if user.lang == "ru" else text.eng
    text = text.format(max_price=max_price, currency = cur_name)
    # text = "Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе\n"  \
    #       f"Введите число от до {max_price}"
    message = await call.message.answer(text=text, reply_markup=await stop_state_keyboard(user))
    await state.update_data(message=message, cur_name=cur_name)


@dp.message_handler(state=SellTonState.min_buy_sum)
async def  min_buy_sum_state(message: types.Message, state: FSMContext):
    '''Продавец ввел мин. сумму для покупки в валюте'''
    user_data = await state.get_data()
    user = await models.User.get(telegram_id=message.chat.id)
    try:
        await user_data['message'].edit_reply_markup(None)
    except aiogram.utils.exceptions.MessageNotModified:
        pass
    min_buy_sum = message.text.replace(',', '.')
    try:
        min_buy_sum = float(min_buy_sum)
        min_buy_sum = float("%.2f" % min_buy_sum)
        if (0.01 < min_buy_sum < user_data['max_price']) is False:
            raise ValueError
    except (ValueError, TypeError):
        text = await models.Lang.get(uuid="04e0b432-a089-473b-9215-562db2af04d1")
        text = text.rus if user.lang == "ru" else text.eng
        text = text.format(max_price=user_data['max_price'], currency=user_data['cur_name'])
        # text = "Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе\n"  \
        #   f"Введите число от до {user_data['max_price']}"
        message = await message.answer(text=text, reply_markup=await stop_state_keyboard(user))
        return await state.update_data(message=message)
    await state.update_data(min_buy_sum=min_buy_sum)
    return await choice_pay_acc_sell_ton_hanlder(message, state)
    

@dp.callback_query_handler(lambda call: call.data == "sell_coin_back_choice_pay_acc", state=SellTonState)
async def choice_pay_acc_sell_ton_hanlder(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    '''Продавец выбирает платежный аккаунт или создает новый'''
    if isinstance(message, types.CallbackQuery):
        message = message.message
        await message.edit_text("Назад")
    user_data = await state.get_data()
    set_user_data = {}
    leave_keys = ['amount', 'fee', 'curreny_name', 'max_price', 'min_buy_sum', 'order_uuid']
    for k,v in user_data.items():
        if k in leave_keys:
            set_user_data[k] = v
    await state.set_data(set_user_data)
    user = await models.User.get(telegram_id=message.chat.id)
    user_payment_accounts = await models.UserPaymentAccount.filter(Q(user=user) & Q(is_active=True) & Q(type__currency__name=user_data['curreny_name']))
    if len(user_payment_accounts) == 0:
        text = await models.Lang.get(uuid="8168939f-31f4-416a-b9e9-896e296f6b34")
        # text = "Создайте хотя бы один аккаунт в выбранной валюте, куда пользователи смогут отправлять вам средства за заказ."
    else:
        text = await models.Lang.get(uuid="e3098392-83e7-4a0e-a8c1-6a44741d7894")
        # text = "Выберите способы оплаты, которые доступны для этого заказа, или создайте новый"
    text = text.rus if user.lang == "ru" else text.eng
    
    currency = await models.Currency.get(name=user_data['curreny_name'])
    if not "order_uuid" in set_user_data:
        order = await models.Order.create(state="created", 
                                        seller=user, 
                                        amount=user_data['amount'],
                                        origin_amount=user_data['amount'],
                                        margin=user_data['fee'], 
                                        commission=user_data['amount'] * 0.01,
                                        currency=currency,
                                        min_buy_sum=user_data['min_buy_sum'])
        user.balance -= user_data['amount']
        user.frozen_balance += user_data['amount']
        await user.save()
        await state.update_data(order_uuid=order.uuid)
    keyboard = await sell_keyboards.add_pay_account_keyboard(user_payment_accounts, user)
    return await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == "sell_coin_add_pay_acc", state=SellTonState)
async def add_pay_account_handler(call: types.CallbackQuery, state: FSMContext):
    '''Кнопка добавить способ оплаты'''
    user = await models.User.get(telegram_id=call.message.chat.id)
    user_data = await state.get_data()
    currency = await models.Currency.get(name=user_data['curreny_name'])
    text = await models.Lang.get(uuid="c8bc4326-82af-406d-8787-b2a461bd6a66")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Выберите тип способа оплаты:"
    await call.message.edit_text("Добавить способ оплаты")
    await call.message.answer(text=text, reply_markup=await payment_account_keyboards.choice_payment_keyboard(callback="sell_coin_pay_type", 
                                                                                                              currency=currency,
                                                                                                              user=user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "sell_coin_choice_pay_acc", state=SellTonState)
async def sell_coin_choice_pay_acc_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    pay_account_id = call.data.split(':')[1]
    
    order = await models.Order.get(uuid=user_data['order_uuid'])
    await models.OrderStateChange.create(order=order, old_state=order.state, new_state='ready_for_sale')
    order.state = 'ready_for_sale'
    await order.save()

    user = await models.User.get(telegram_id=call.message.chat.id)
    if pay_account_id == 'all':
        await call.message.edit_text("Выбрать все")
        pay_accounts = await models.UserPaymentAccount.filter(Q(user=user) & Q(is_active=True) & Q(type__currency=await order.currency))
    else:
        pay_accounts = [await models.UserPaymentAccount.get(serial_int=pay_account_id)]
        pay_type = await pay_accounts[0].type
        
        name = await lang_payment_type(pay_type)
        await call.message.edit_text(name)
    for account in pay_accounts:
        await models.OrderUserPaymentAccount.create(order=order,
                                                    account=account,
                                                    is_active=True)
    
    await user.save()
    await state.finish()
    text = await models.Lang.get(uuid="697085d7-ebfd-4756-9425-7f0b160b41af")
    text = text.rus if user.lang == "ru" else text.eng
    text = text.format(order_uuid=order.serial_int, 
                       order_amount=order.amount - order.commission)
    # text =f"Ваш заказ № {order.uuid} успешно опубликован.\n"  \
    #        "Комиссия за продажу равна 1% в TonCoin\n"  \
    #       f"Таким образом финальное количество продаваемых TonCoin равно {order.amount - order.commission}\n"  \
    #        "Как только покупатель будет найден, мы отправим вам сообщение.\n"  \
    #        "Если вы хотите отменить заказ, можете сделать это в интерфейсе Мои заказы\n"
    await call.message.answer(text)