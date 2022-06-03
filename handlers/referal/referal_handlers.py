from loader import dp
from aiogram import types
from models import models
from keyboards.inline import referal_keyboards
@dp.message_handler(regexp="^(Реферальная система)$")
async def referal_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = f"Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с "  \
            "вашим реферальным кодов {{ uuid текущего User }}, то вы получите 1 Toncoin на ваш счет"
    await message.answer(text=text, reply_markup=referal_keyboards.referal_keyboard(user.uuid))