from keyboards.inline import payment_account_keyboards
from loader import dp
from aiogram import types
from typing import Union
from models import models
from utils import lang


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

    type_name = await lang.lang_payment_type(payment_type=payment_type, 
                                        user=user)
    
    
    cur = await payment_type.currency
    cur_name = await lang.lang_currency(currency=cur, 
                                   user=user)

    user_data_text = ""
    for k,v in pay_account.data.items():
        user_data_text += f"{k}: {v}\n"

    text = await lang.lang_text(lang_uuid="50407743-511d-4f95-bad9-36dc5e69e433",
                           user=user,
                           format={
                                "cur_name":cur_name,
                                "type_name":type_name,
                                "user_data_text":user_data_text        
                           })    
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