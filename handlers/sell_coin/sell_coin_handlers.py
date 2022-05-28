import decimal
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import sell_keyboards
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from utils.validate_ton_address import get_currency_ton

class SellTonState(StatesGroup):
    amount = State()
    fee = State()
    currency = State()
    

@dp.message_handler(regexp="^(Продать Ton)$")
async def sell_ton_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    # print(user.permission_balance)
    # permission_balance = user.balance - user.frozen_balance
    if user.permission_balance < 0.1:
        text = "Пополните баланс для создания заказа на продажу TonCoin"
        return await message.answer(text=text)
    await SellTonState.amount.set()
    text = f"Введите количество TON, которое вы хотите продать (число от 0.1 до {user.permission_balance})"
    return await message.answer(text)


@dp.message_handler(state=SellTonState.amount, content_types=['text'])
async def sell_ton_state(message: types.Message, state: FSMContext):
    amount = message.text.replace(',', '.')
    user = await models.User.get(telegram_id=message.chat.id)
    try:
        amount = float(amount)
        if amount > user.permission_balance:
            raise ValueError
    except (ValueError, TypeError):
        text = f"Неверный формат ввода. Введите число от 0.1 до {user.permission_balance}"
        return await message.answer(text)
    
    text = "Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100\n"  \
           "Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap"
    await state.update_data(amount=amount)
    await SellTonState.next()
    return await message.answer(text=text)


@dp.message_handler(state=SellTonState.fee, content_types=['text'])
async def fee_state(message: types.Message, state:FSMContext):
    fee = message.text.replace(',', '.')
    try:
        fee = float(fee)
        if (1 <= fee <= 100) is False:
            raise ValueError 
    except (ValueError, TypeError):
        text = "Неверный формат ввода. Введите число от 1 до 100"
        return await message.answer(text)
    await state.update_data(fee=fee)
    await SellTonState.next()
    text = "Выберите валюту, в которой вы хотите продать TonCoin:"
    reply_markup = await sell_keyboards.currency_keyboard()
    await message.answer(text=text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'currency', state=SellTonState.currency)
async def choice_currency_state(call: types.CallbackQuery, state: FSMContext):
    
    # await SellTonState.next()
    ton_currency = await get_currency_ton()
    user_data = await state.get_data()
    currency = await models.Currency.get(name=call.data.split(':')[1])
    max_price = "%.2f" % (float(user_data['amount']) * float(ton_currency) * float(currency.exchange_rate))
    await state.update_data(curreny_name=call.data.split(':')[1], max_price=max_price)
    text = "Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе\n"  \
          f"Введите число от до {max_price}"
    return await call.message.answer(text=text)




    

