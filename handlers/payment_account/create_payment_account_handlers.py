from handlers.sell_coin.sell_coin_handlers import choice_pay_acc_sell_ton_hanlder
from handlers.sell_coin.state import SellTonState
from keyboards.inline import currency_keyboards, payment_account_keyboards
from keyboards.inline.keyboards import stop_state_keyboard
from loader import dp
from models import models
from utils import lang
from aiogram import types
from .state import PaymentAccountState
from aiogram.dispatcher import FSMContext
from .view_payment_account_handlers import view_pay_account
from tortoise.queryset import Q

@dp.callback_query_handler(lambda call: call.data == 'add_payment_account')
async def add_payment_account_handler(call: types.CallbackQuery):
    '''Мои счета -> Добавить способ оплаты
       Выбор валюты
    '''
    user = await models.User.get(telegram_id=call.message.chat.id)
    
    edit_text = await lang.lang_text(lang_uuid="953216e7-3945-490e-bd71-8aab610857f6",
                                user=user)
    await call.message.edit_text(edit_text)
    
    allow_currency_count = await models.Currency.filter(Q(is_active=True) & Q(user_payment_account_type__is_active=True)).count()
    if allow_currency_count > 0:
        text = await lang.lang_text(lang_uuid="f2bdd4ea-71c6-4d8c-9e2b-1875ebbe7403",       # text = "Выберите валюту способа оплаты:"
                           user=user)
    else:
        text = await lang.lang_text(lang_uuid="b9d67810-9adf-4ae4-99b3-ca9e42225396",       # text = "Нет доступных валют"
                           user=user)
    
    return await call.message.answer(text=text, reply_markup=await currency_keyboards.currency_keyboard(callback="add_cur_pay_acc",
                                                                                                        user=user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_cur_pay_acc')
async def choice_currency_payment_account_hanlder(call: types.CallbackQuery):
    '''Мои счета -> Добавить способ оплаты -> {валюта}
       Выбор платежного типа
    '''
    user = await models.User.get(telegram_id=call.message.chat.id)
    cur_name = call.data.split(':')[1]
    currency = await models.Currency.get(name=cur_name)
    cur_name = await lang.lang_currency(currency=currency, 
                                   user=user)
    
    edit_text = await lang.lang_text(lang_uuid="93a3e2ea-a462-462a-8fca-a3689d3d0690",
                                user=user,
                                format={
                                    "cur_name":cur_name   
                                })
    await call.message.edit_text(edit_text)
    currency_type_payments_count = await models.UserPaymentAccountType.filter(Q(currency=currency) & Q(is_active=True)).count()
    if currency_type_payments_count > 0:
        text = await lang.lang_text(lang_uuid="9aee8627-5946-466c-bf64-231d4170c34f",  # text = "Выберите тип способа оплаты:"
                                    user=user)
    else:
        text = await lang.lang_text(lang_uuid="bd8a275e-e8f5-4268-8186-5da5a3cd4bd9",  # text = "Нет достпуных платежных типов"
                                    user=user)
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
    type_name = await lang.lang_payment_type(payment_type=payment_type, 
                                        user=user)
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
    
    text = await lang.lang_text(lang_uuid="8a33cc94-7dff-468a-bdaa-2bfef60406b2",
                           user=user,
                           format={
                                "payment_type_data_value":payment_type_data_list[0]        
                           })
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
        
        text = await lang.lang_text(lang_uuid="8a33cc94-7dff-468a-bdaa-2bfef60406b2",
                           user=user,
                           format={
                                "payment_type_data_value":next_data     
                           })
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
