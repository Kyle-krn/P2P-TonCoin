from .payment_account_handlers import payment_account_message_handler
from loader import dp
from aiogram import types
from models import models
from utils import lang

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'del_pay_acc')
async def delete_pay_account_hanlder(call: types.CallbackQuery):
    pay_acc_serial_int = call.data.split(':')[1]
    pay_account = await models.UserPaymentAccount.get(serial_int=pay_acc_serial_int)
    pay_account.is_active = False
    await pay_account.save()
    user = await models.User.get(tg_id=call.message.chat.id)
    edit_text = await lang.lang_text(lang_uuid="f4059557-00c3-45fe-81d8-8d132dc16698",
                                user=user)
    await call.message.edit_text(edit_text)
    return await payment_account_message_handler(call.message)
