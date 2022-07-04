from typing import Union
from keyboards.inline.keyboards import stop_state_keyboard
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import payment_account_keyboards
from keyboards.inline import currency_keyboards
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from handlers.sell_coin.sell_coin_handlers import choice_pay_acc_sell_ton_hanlder
from handlers.sell_coin.state import SellTonState 



class PaymentAccountState(StatesGroup):
    data = State()

@dp.message_handler(regexp="^(Мои счета)$")
@dp.message_handler(regexp="^(My bank account)$")
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_my_pay_account')
async def payment_account_message_handler(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        message = message.message
        await message.edit_text("Назад")
    user = await models.User.get(telegram_id=message.chat.id)
    text = await models.Lang.get(uuid="38cf9afe-083a-4e90-a29c-a743cc6895fa")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Выберите ваш способ оплаты для изменения или добавьте новый"
    message_kwargs = {"text": text, 
                      "reply_markup": await payment_account_keyboards.list_payment_account_keyboard(user)}
    return await message.answer(**message_kwargs)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'view_pay_acc')
async def view_pay_account(message: Union[types.CallbackQuery, types.Message], pay_account_serial_int: int = None):
    '''Просмотр платежного аккаунта'''
    
    if pay_account_serial_int is None:
        pay_account_serial_int = message.data.split(':')[1]
        chat_id = message.message.chat.id
    else:
        chat_id = message.chat.id
    user = await models.User.get(telegram_id=chat_id)
    pay_account = await models.UserPaymentAccount.get(serial_int=pay_account_serial_int)
    payment_type = await pay_account.type
    type_name = payment_type.name
    lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=payment_type.uuid)
    if lang_type:
        type_name = lang_type.rus if user.lang == 'ru' else lang_type.eng
    
    cur = await payment_type.currency
    cur_name = cur.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=cur.uuid)
    if lang_cur:
        cur_name = lang_cur.rus if user.lang == 'ru' else lang_cur.eng

    user_data_text = ""
    for k,v in pay_account.data.items():
        user_data_text += f"{k}: {v}\n"
        
    text = await models.Lang.get(uuid="50407743-511d-4f95-bad9-36dc5e69e433")
    text = text.rus if user.lang == "ru" else text.eng
    text = text.format(cur_name=cur_name, 
                       type_name=type_name, 
                       user_data_text=user_data_text)
    # text =f"Валюта: {cur_name}\n"  \
    #       f"Тип оплаты: {type_name}\n"  \
    #       f"{user_data_text}"
    keyboard = await payment_account_keyboards.pay_account_control_keyboard(payment_type_serial_int=payment_type.serial_int, 
                                                                            payment_acc_serial_int=pay_account.serial_int,
                                                                            user=user)
    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text(type_name)
        return await message.message.answer(text=text, reply_markup=keyboard)
    else:
        return await message.answer(text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == 'add_payment_account')
async def add_payment_account_handler(call: types.CallbackQuery):
    await call.message.edit_text("Добавить способ оплаты")
    user = await models.User.get(telegram_id=call.message.chat.id)
    text = await models.Lang.get(uuid="f2bdd4ea-71c6-4d8c-9e2b-1875ebbe7403")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Выберите валюту способа оплаты:"
    return await call.message.answer(text=text, reply_markup=await currency_keyboards.currency_keyboard(callback="add_cur_pay_acc",
                                                                                                        user=user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_cur_pay_acc')
async def choice_currency_payment_account_hanlder(call: types.CallbackQuery):
    cur_name = call.data.split(':')[1]
    currency = await models.Currency.get(name=cur_name)
    cur_name = currency.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
    if lang_cur:
        cur_name = lang_cur.rus
    await call.message.edit_text(f"Вы выбрали {cur_name}")
    user = await models.User.get(telegram_id=call.message.chat.id)
    text = await models.Lang.get(uuid="f2bdd4ea-71c6-4d8c-9e2b-1875ebbe7403")
    text = text.rus if user.lang == "ru" else text.eng
    
    
    # text = "Выберите тип способа оплаты:"
    await call.message.answer(text=text, reply_markup=await payment_account_keyboards.choice_payment_keyboard(callback="pay_type",
                                                                                                              currency=currency,
                                                                                                              user=user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'pay_type')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'change_pay_acc')
@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "sell_coin_pay_type", state=SellTonState)
async def set_state_data_pay_type_handler(call: types.CallbackQuery, state: FSMContext):
    pay_type_serial_int = call.data.split(':')[1]
    user = await models.User.get(telegram_id=call.message.chat.id)
    payment_type = await models.UserPaymentAccountType.get(serial_int=pay_type_serial_int)
    type_name = payment_type.name
    lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=payment_type.uuid)
    if lang_type:
        type_name = lang_type.rus
    await call.message.edit_text(text=type_name)
    payment_type_data_list = [i for i in payment_type.data]
    if call.data.split(':')[0] in ['pay_type', 'change_pay_acc']:
        await PaymentAccountState.data.set()
        state = dp.get_current().current_state()
        update_data_kwargs = {"payment_type": payment_type.serial_int}
        if call.data.split(':')[0] == "change_pay_acc":
            update_data_kwargs['pay_account'] = call.data.split(':')[2]
        await state.update_data(**update_data_kwargs)
    else:
        await SellTonState.pay_acc_data.set()
        await state.update_data(payment_type=payment_type.serial_int)
    text = await models.Lang.get(uuid="8a33cc94-7dff-468a-bdaa-2bfef60406b2")
    text = text.rus if user.lang == "ru" else text.eng
    text = text.format(payment_type_data_value=payment_type_data_list[0])
    # text = f"Введите {payment_type_data_list[0]}:"
    await call.message.answer(text=text, reply_markup=await stop_state_keyboard(user))


@dp.message_handler(state=PaymentAccountState.data)
@dp.message_handler(state=SellTonState.pay_acc_data)
async def add_data_state(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user = await models.User.get(telegram_id=message.chat.id)
    if 'payment_type' not in user_data:
        return
    payment_type = await models.UserPaymentAccountType.get(serial_int=user_data['payment_type'])
    payment_type_data_list = [i for i in payment_type.data]
    current_state = await state.get_state()
    for item in payment_type_data_list:
        if item not in user_data:
            kwargs = {item:message.text}
            await state.update_data(**kwargs)
            break

    user_data = await state.get_data() 
    next_data = None
    for item in payment_type_data_list:
        if item not in user_data:
            next_data = item
            break

    if next_data:
        text = await models.Lang.get(uuid="8a33cc94-7dff-468a-bdaa-2bfef60406b2")
        text = text.rus if user.lang == "ru" else text.eng
        text = text.format(payment_type_data_value=next_data)
        # text = f"Введите {next_data}:"
        return await message.answer(text=text, reply_markup=await stop_state_keyboard(user))
    else:
        
        if current_state.split(':')[0] == "PaymentAccountState":
            await state.finish()
            del user_data['payment_type']
            if 'pay_account' in user_data:
                pay_account = await models.UserPaymentAccount.get(serial_int=user_data['pay_account'])
                del user_data['pay_account']
                pay_account.data = user_data
                await pay_account.save()
            else:
                pay_account = await models.UserPaymentAccount.create(user=user, type=payment_type, data=user_data, is_active=True)
            return await view_pay_account(message, pay_account_serial_int=pay_account.serial_int)
        elif current_state.split(':')[0] == "SellTonState":
            del_keys = ['amount', 'fee', 'curreny_name', 'max_price', 'min_buy_sum', 'payment_type', 'order_uuid']
            for key in del_keys:
                user_data.pop(key, None)
            pay_account = await models.UserPaymentAccount.create(user=user, type=payment_type, data=user_data, is_active=True)
            return await choice_pay_acc_sell_ton_hanlder(message, state)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'del_pay_acc')
async def delete_pay_account_hanlder(call: types.CallbackQuery):
    pay_acc_serial_int = call.data.split(':')[1]
    pay_account = await models.UserPaymentAccount.get(serial_int=pay_acc_serial_int)
    pay_account.is_active = False
    await pay_account.save()
    await call.message.edit_text("Успешно удалено")
    return await payment_account_message_handler(call.message)
