from loader import dp
from aiogram import types
from models import models
from keyboards.inline import wallet_keyboards
from aiogram.dispatcher import FSMContext
from utils.lang import lang_text
from utils.validate_ton_address import validate_wallet
from .state import WithdrawState
from utils.generate_code import generate_code



@dp.message_handler(regexp=f"^(Кошелек)$")
@dp.message_handler(regexp=f"^(Wallet)$")
async def main_wallet_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = await lang_text(lang_uuid="de220ffc-1210-4433-a681-76c30a829ca7", 
                           user=user, 
                           format={
                                    "balance": "%.4f" % user.balance,
                                    "frozen_balance": "%.4f" % user.frozen_balance
                                  })
    # text = "Кошелёк\n\n" \
    #        f"Баланс Toncoin: {user.balance} TON\n"  \
    #        f"Заморожено в заказах на продажу Toncoin: {user.frozen_balance} TON"
    await message.answer(text=text, reply_markup=await wallet_keyboards.main_wallet_keyboard(user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'top_up')
async def top_up_wallet_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    code = await generate_code()
    await models.UserBalanceChange.create(user=user,
                                          type="topup",
                                          state="created", 
                                          code=code)
    
    text = await lang_text(lang_uuid="c8b08b1b-8dfc-484f-a0c5-b106e2958bf5",
                           user=user,
                           format={
                               "code": code,
                               "address_smart_contract": "Потом вставить адрес контракта"
                           })
    # text = "Используйте адрес ниже для пополнения баланса TON.\n\n" \
    #        "Сеть: The Open Network – TON\n\n"  \
    #        "{{ наш адрес смарт-контракта }}\n\n"  \
    #       f"ОБЯЗАТЕЛЬНО укажите код <b>{code}</b> в комментарии при пополнении баланса. Без этого кода ваше пополнение баланса может не отразиться в системе"
    return await call.message.answer(text=text)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'withdraw')
async def withdraw_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    # permission_balance = user.balance - user.frozen_balance
    if user.permission_balance > 0:
        text = await lang_text(lang_uuid="34cff16d-6bd5-4eb1-ae12-3655095511fc",
                               user=user,
                               format={
                                   "permission_balance":user.permission_balance
                               })
        # text = f"Для вывода доступно {user.permission_balance} TON\n"  \
        #        f"Отправьте количество TON, которое вы хотите вывести (не более {user.permission_balance} TON)"
        await WithdrawState.amount.set()
    else:
        text = await lang_text(lang_uuid="9f1a916e-ffaa-4dfc-9e90-d6935492561c",
                               user=user)
        # text = f"На вашем балансе нет средств."
    return await call.message.answer(text=text)


@dp.message_handler(state=WithdrawState.amount, content_types=['text'])
async def withdraw_amount_state(message: types.Message, state: FSMContext):
    user = await models.User.get(telegram_id=message.chat.id)
    try:
        withdraw_amount = float(message.text)
        if withdraw_amount > user.permission_balance:
            raise ValueError
    except (ValueError, TypeError):
        text = await lang_text(lang_uuid="34cff16d-6bd5-4eb1-ae12-3655095511fc",
                               user=user,
                               format={
                                    "permission_balance":user.permission_balance        
                               })
        # text = f"Для вывода доступно {user.permission_balance} TON\n"  \
        #        f"Отправьте количество TON, которое вы хотите вывести (не более {user.permission_balance} TON)"
        return await message.answer(text=text)
    await state.update_data(withdraw_amount=withdraw_amount)
    await WithdrawState.next()
    text = await lang_text(lang_uuid="b18512b1-9e18-4fda-ac00-ab2f45bf323b",
                           user=user,
                           format={
                                "withdraw_amount":withdraw_amount        
                           })
    # text = f"Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON"
    return await message.answer(text=text)


@dp.message_handler(state=WithdrawState.ton_wallet, content_types=['text'])
async def ton_wallet_state(message: types.Message, state: FSMContext):
    wallet = message.text
    res = await validate_wallet(wallet)
    user_data = await state.get_data()
    user = await models.User.get(telegram_id=message.chat.id)
    if res['ok'] is False:
        text = await lang_text(lang_uuid="b18512b1-9e18-4fda-ac00-ab2f45bf323b",
                           user=user,
                           format={
                                "withdraw_amount":user_data['withdraw_amount']        
                           })
        # text = f"Введите номер кошелька, на который вы хотите вывести {user_data['withdraw_amount']} TON"
        return await message.answer(text=text)
    
    await models.UserBalanceChange.create(user=user,
                                          type="withdraw",
                                          amount=user_data['withdraw_amount'], 
                                          wallet=wallet,
                                          state="created")
    user.balance = user.balance - user_data['withdraw_amount']
    await user.save()
    await state.finish()
    text = await lang_text(lang_uuid="ad436ce0-a56a-4022-9222-9fc309b23c82",
                           user=user,
                           format={
                                "amount":user_data['withdraw_amount'],
                                "balance":user.balance    
                           })
    #     Вывод средств на сумму {{ amount }} TON успешно выполнен! 
        # Ваш баланс: {{ balance }} TON
    await message.answer(text)

