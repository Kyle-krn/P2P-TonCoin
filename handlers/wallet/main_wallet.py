from loader import dp
from aiogram import types
from models import models
from keyboards.inline import wallet_keyboards
from aiogram.dispatcher import FSMContext
from utils.validate_ton_address import validate_wallet
from .state import WithdrawState
# from utils.message_handler_filter import ru_wallet_filter, eng_wallet_filter
from utils.generate_code import generate_code



@dp.message_handler(regexp=f"^(Кошелек)$")
async def main_wallet_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = await models.Lang.get(uuid="a09a0580-6b61-4011-963d-e83abb427b67")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(balance=user.balance, frozen_balance=user.frozen_balance)
    # text = "Кошелёк\n\n" \
    #        f"Баланс Toncoin: {user.balance} TON\n"  \
    #        f"Заморожено в заказах на продажу Toncoin: {user.frozen_balance} TON"
    await message.answer(text=text, reply_markup=await wallet_keyboards.main_wallet_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'top_up')
async def top_up_wallet_handler(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    code = await generate_code()
    await models.UserBalanceChange.create(user=user,
                                          type="topup",
                                          state="created", 
                                          code=code)
    text = await models.Lang.get(uuid="5b6bf9ee-37b9-4db9-b6a6-443ca67ad30f")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(code=code, address_smart_contract="Потом вставить адрес контракта")
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
        text = await models.Lang.get(uuid="eb70f41c-0aae-4a44-ab1b-485491e64841")
        text = text.rus if user.lang == 'ru' else text.eng
        text = text.format(permission_balance=user.permission_balance)
        # text = f"Для вывода доступно {user.permission_balance} TON\n"  \
        #        f"Отправьте количество TON, которое вы хотите вывести (не более {user.permission_balance} TON)"
        await WithdrawState.amount.set()
    else:
        text = await models.Lang.get(uuid="afe8f688-4ec8-4eb5-8597-aefbc44a0170")
        text = text.rus if user.lang == 'ru' else text.eng
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
        text = await models.Lang.get(uuid="eb70f41c-0aae-4a44-ab1b-485491e64841")
        text = text.rus if user.lang == 'ru' else text.eng
        text = text.format(permission_balance=user.permission_balance)
        # text = f"Для вывода доступно {user.permission_balance} TON\n"  \
        #        f"Отправьте количество TON, которое вы хотите вывести (не более {user.permission_balance} TON)"
        return await message.answer(text=text)
    await state.update_data(withdraw_amount=withdraw_amount)
    await WithdrawState.next()
    text = await models.Lang.get(uuid="cb284258-a311-4c37-a23d-ed9ee2b68023")
    text = text.rus if user.lang == 'ru' else text.eng
    text = text.format(withdraw_amount=withdraw_amount)
    # text = f"Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON"
    return await message.answer(text=text)


@dp.message_handler(state=WithdrawState.ton_wallet, content_types=['text'])
async def ton_wallet_state(message: types.Message, state: FSMContext):
    wallet = message.text
    res = await validate_wallet(wallet)
    user_data = await state.get_data()
    user = await models.User.get(telegram_id=message.chat.id)
    if res['ok'] is False:
        text = await models.Lang.get(uuid="cb284258-a311-4c37-a23d-ed9ee2b68023")
        text = text.rus if user.lang == 'ru' else text.eng
        text = text.format(withdraw_amount=user_data['withdraw_amount'])
    
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
    text = await models.Lang.get(uuid="0ac73992-32a1-4890-8a17-011de83ef039")
    text = text.rus if user.lang == 'ru' else text.eng
    await message.answer(text)

