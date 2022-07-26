from typing import Union
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import payment_account_keyboards
from utils.lang import lang_text 
from tortoise.exceptions import DoesNotExist
from handlers.start import start

@dp.message_handler(regexp="^(Мои счета)$")
@dp.message_handler(regexp="^(My bank account)$")
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_my_pay_account')
async def payment_account_message_handler(message: Union[types.Message, types.CallbackQuery]):
    if isinstance(message, types.CallbackQuery):
        message = message.message
        user = await models.User.get(telegram_id=message.chat.id)
        edit_text = await lang_text(lang_uuid="eef933b0-e3bc-46ed-8461-8226fd5f090f",
                                    user=user)
        await message.edit_text(edit_text)
    else:
        try:
            user = await models.User.get(telegram_id=message.chat.id)
        except DoesNotExist:
            return await start(message)
    text = await lang_text(lang_uuid="38cf9afe-083a-4e90-a29c-a743cc6895fa",
                           user=user)
    # text = "Выберите ваш способ оплаты для изменения или добавьте новый"
    message_kwargs = {"text": text, 
                      "reply_markup": await payment_account_keyboards.list_payment_account_keyboard(user)}
    return await message.answer(**message_kwargs)






