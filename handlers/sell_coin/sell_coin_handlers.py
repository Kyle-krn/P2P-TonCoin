from typing import Union
import aiogram
from keyboards.inline.keyboards import stop_state_keyboard
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import currency_keyboards, payment_account_keyboards
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from tortoise.queryset import Q
from utils.validate_ton_address import get_currency_ton
from keyboards.inline import sell_keyboards


class SellTonState(StatesGroup):
    amount = State()
    fee = State()
    currency = State()
    min_buy_sum = State()
    pay_acc_data = State()


@dp.message_handler(regexp="^(Продать Ton)$")
async def sell_ton_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    if user.balance < 0.1:
        text = "Пополните баланс для создания заказа на продажу TonCoin"
        return await message.answer(text=text)
    await SellTonState.amount.set()
    state = dp.get_current().current_state()
    text = f"Введите количество TON, которое вы хотите продать (число от 0.1 до {user.balance})"
    message = await message.answer(text, reply_markup=await stop_state_keyboard())
    await state.update_data(message=message)


@dp.message_handler(state=SellTonState.amount, content_types=['text'])
async def sell_ton_state(message: types.Message, state: FSMContext):
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
        text = f"Неверный формат ввода. Введите число от 0.1 до {user.balance}"
        message = await message.answer(text, reply_markup=await stop_state_keyboard())
        return await state.update_data(message=message)

    text = "Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100\n"  \
           "Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap"
    await state.update_data(amount=amount)
    await SellTonState.next()
    message = await message.answer(text=text, reply_markup=await stop_state_keyboard())
    await state.update_data(message=message)


@dp.message_handler(state=SellTonState.fee, content_types=['text'])
async def fee_state(message: types.Message, state:FSMContext):
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
        text = "Неверный формат ввода. Введите число от 1 до 100"
        message = await message.answer(text)
        return await state.update_data(message=message)
    await state.update_data(fee=fee)
    await SellTonState.next()
    text = "Выберите валюту, в которой вы хотите продать TonCoin:"
    reply_markup = await currency_keyboards.currency_keyboard(callback="sell_coin_currency")
    message = await message.answer(text=text, reply_markup=reply_markup)
    await state.update_data(message=message)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'sell_coin_currency', state=SellTonState.currency)
async def choice_currency_state(call: types.CallbackQuery, state: FSMContext):
    await SellTonState.next()
    ton_currency = await get_currency_ton()
    user_data = await state.get_data()
    currency = await models.Currency.get(name=call.data.split(':')[1])
    cur_name = currency.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
    if lang_cur:
        cur_name = lang_cur.rus
    await user_data['message'].edit_text(text=f"Вы выбрали: {cur_name}")
    max_price = float("%.2f" % (float(user_data['amount']) * float(ton_currency) * float(currency.exchange_rate)))
    await state.update_data(curreny_name=call.data.split(':')[1], max_price=max_price)
    text = "Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе\n"  \
          f"Введите число от до {max_price}"
    message = await call.message.answer(text=text, reply_markup=await stop_state_keyboard())
    await state.update_data(message=message)

@dp.message_handler(state=SellTonState.min_buy_sum)
async def  min_buy_sum_state(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    try:
        await user_data['message'].edit_reply_markup(None)
    except aiogram.utils.exceptions.MessageNotModified:
        pass
    min_buy_sum = message.text.replace(',', '.')
    try:
        min_buy_sum = float(min_buy_sum)
        min_buy_sum = float("%.2f" % min_buy_sum)
        if (0 < min_buy_sum < user_data['max_price']) is False:
            raise ValueError
    except (ValueError, TypeError):
        text = "Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе\n"  \
          f"Введите число от до {user_data['max_price']}"
        message = await message.answer(text=text, reply_markup=await stop_state_keyboard())
        return await state.update_data(message=message)
    await state.update_data(min_buy_sum=min_buy_sum)
    return await choice_pay_acc_sell_ton_hanlder(message, state)
    

@dp.callback_query_handler(lambda call: call.data == "sell_coin_back_choice_pay_acc", state=SellTonState)
async def choice_pay_acc_sell_ton_hanlder(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    # call = None
    if isinstance(message, types.CallbackQuery):
        message = message.message
        await message.edit_text("Назад")
    user_data = await state.get_data()
    set_user_data = {}
    leave_keys = ['amount', 'fee', 'curreny_name', 'max_price', 'min_buy_sum']
    for k,v in user_data.items():
        if k in leave_keys:
            set_user_data[k] = v
    await state.set_data(set_user_data)
    user = await models.User.get(telegram_id=message.chat.id)
    user_payment_accounts = await models.UserPaymentAccount.filter(Q(user=user) & Q(is_active=True) & Q(type__currency__name=user_data['curreny_name']))
    if len(user_payment_accounts) == 0:
        text = "Создайте хотя бы один аккаунт в выбранной валюте, куда пользователи смогут отправлять вам средства за заказ."
    else:
        text = "Выберите способы оплаты, которые доступны для этого заказа, или создайте новый"
    keyboard = await sell_keyboards.add_pay_account_keyboard(user_payment_accounts)
    return await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == "sell_coin_add_pay_acc", state=SellTonState)
async def add_pay_account_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    currency = await models.Currency.get(name=user_data['curreny_name'])
    text = "Выберите тип способа оплаты:"
    await call.message.edit_text("Добавить способ оплаты")
    await call.message.answer(text=text, reply_markup=await payment_account_keyboards.choice_payment_keyboard(callback="sell_coin_pay_type", currency=currency))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == "sell_coin_choice_pay_acc", state=SellTonState)
async def sell_coin_choice_pay_acc_handler(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    pay_account_id = call.data.split(':')[1]
    user = await models.User.get(telegram_id=call.message.chat.id)
    if pay_account_id == 'all':
        await call.message.edit_text("Выбрать все")
        pay_accounts = await models.UserPaymentAccount.filter(Q(user=user) & Q(is_active=True) & Q(type__currency__name=user_data['curreny_name']))
    else:
        pay_accounts = [await models.UserPaymentAccount.get(serial_int=pay_account_id)]
        pay_type = await pay_accounts[0].type
        name = pay_type.name
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=pay_type.uuid)
        if lang_type:
            name = lang_type.rus
        await call.message.edit_text(name)
    currency = await models.Currency.get(name=user_data['curreny_name'])
    order = await models.Order.create(state="ready_for_sale", 
                                      seller=user, 
                                      amount=user_data['amount'],
                                      origin_amount=user_data['amount'],
                                      margin=user_data['fee'], 
                                      commission=user_data['amount'] * 0.01,
                                      currency=currency,
                                      min_buy_sum=user_data['min_buy_sum'])
    for account in pay_accounts:
        await models.OrderUserPaymentAccount.create(order=order,
                                                    account=account,
                                                    is_active=True)
    user.balance -= user_data['amount']
    user.frozen_balance += user_data['amount']
    await user.save()
    await state.finish()
    text =f"Ваш заказ № {order.uuid} успешно опубликован.\n"  \
           "Комиссия за продажу равна 1% в TonCoin\n"  \
          f"Таким образом финальное количество продаваемых TonCoin равно {order.amount - order.commission}\n"  \
           "Как только покупатель будет найден, мы отправим вам сообщение.\n"  \
           "Если вы хотите отменить заказ, можете сделать это в интерфейсе Мои заказы\n"
    await call.message.answer(text)