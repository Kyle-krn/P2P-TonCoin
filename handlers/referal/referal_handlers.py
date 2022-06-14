from loader import dp
from aiogram import types
from models import models
from keyboards.inline import referal_keyboards

@dp.message_handler(regexp="^(Реферальная система)$")
async def referal_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = await models.Lang.get(uuid="dd9796b9-8476-4092-aa51-796a15a3a565")
    text = text.rus if user.lang == "ru" else text.eng
    text = text.format(link=f"https://t.me/TonCoinTestBot?start={user.uuid}")
#     text = f"Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с "  \
#             "вашим реферальным кодов {{ uuid текущего User }}, то вы получите 1 Toncoin на ваш счет"
    await message.answer(text=text, reply_markup=referal_keyboards.referal_keyboard(user.uuid))