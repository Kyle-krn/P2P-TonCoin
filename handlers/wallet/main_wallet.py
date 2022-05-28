from email.headerregistry import Group
import secrets
import string
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import wallet_keyboards
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from utils.validate_ton_address import validate_wallet
class WithdrawState(StatesGroup):
    amount = State()
    ton_wallet = State()


def random_string():
    res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(5))  
    return res

async def generate_code():
    return f"{random_string()}-{random_string()}-{random_string()}-{random_string()}"

@dp.message_handler(regexp="^(Кошелек)$")
async def main_wallet_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = "Кошелёк\n\n" \
           f"Баланс Toncoin: {user.balance} TON\n"  \
           f"Заморожено в заказах на продажу Toncoin: {user.frozen_balance} TON"
    await message.answer(text=text, reply_markup=await wallet_keyboards.main_wallet_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'top_up')
async def top_up_wallet_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    code = await generate_code()
    await models.UserBalanceChange.create(user=user,
                                          type="topup",
                                          state="created", 
                                          code=code)
    text = "Используйте адрес ниже для пополнения баланса TON.\n\n" \
           "Сеть: The Open Network – TON\n\n"  \
           "{{ наш адрес смарт-контракта }}\n\n"  \
          f"ОБЯЗАТЕЛЬНО укажите код <b>{code}</b> в комментарии при пополнении баланса. Без этого кода ваше пополнение баланса может не отразиться в системе"
    return await call.message.answer(text=text)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'withdraw')
async def withdraw_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    # permission_balance = user.balance - user.frozen_balance
    if user.permission_balance > 0:
        text = f"Для вывода доступно {user.permission_balance} TON\n"  \
               f"Отправьте количество TON, которое вы хотите вывести (не более {user.permission_balance} TON)"
        await WithdrawState.amount.set()
    else:
        text = f"На вашем балансе нет средств."
    return await call.message.answer(text=text)

@dp.message_handler(state=WithdrawState.amount, content_types=['text'])
async def withdraw_amount_state(message: types.Message, state: FSMContext):
    user = await models.User.get(telegram_id=message.chat.id)
    # permission_balance = user.balance - user.frozen_balance
    try:
        withdraw_amount = float(message.text)
        if withdraw_amount > user.permission_balance:
            raise ValueError
    except (ValueError, TypeError):
        text = f"Для вывода доступно {user.permission_balance} TON\n"  \
               f"Отправьте количество TON, которое вы хотите вывести (не более {user.permission_balance} TON)"
        return await message.answer(text=text)
    await state.update_data(withdraw_amount=withdraw_amount)
    await WithdrawState.next()
    text = f"Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON"
    return await message.answer(text=text)


@dp.message_handler(state=WithdrawState.ton_wallet, content_types=['text'])
async def ton_wallet_state(message: types.Message, state: FSMContext):
    wallet = message.text
    res = await validate_wallet(wallet)
    user_data = await state.get_data()
    if res['ok'] is False:
        text = f"Введите номер кошелька, на который вы хотите вывести {user_data['withdraw_amount']} TON"
        return await message.answer(text=text)
    user = await models.User.get(telegram_id=message.chat.id)
    await models.UserBalanceChange.create(user=user,
                                          type="withdraw",
                                          amount=user_data['withdraw_amount'], 
                                          wallet=wallet,
                                          state="created")
    user.balance = user.balance - user_data['withdraw_amount']
    await user.save()
    await state.finish()
    text = "Ваш запрос зарегистрирован, мы пришлем сообщение, когда вывод будет осуществлен."
    await message.answer(text)

