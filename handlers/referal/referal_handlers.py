from loader import dp
from aiogram import types
from models import models
from keyboards.inline import referal_keyboards
from utils.lang import lang_text

@dp.message_handler(regexp="^(Реферальная система)$")
@dp.message_handler(regexp="^(Referal system)$")
async def referal_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)

    text = await lang_text(lang_uuid="3765be5b-239f-4299-960a-369fd34fef96",
                           user=user,
                           format={
                               "link":f"https://t.me/TonCoinTestBot?start={user.uuid}"
                           })
    #     text = f"Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с "  \
#             "вашим реферальным кодов {{ uuid текущего User }}, то вы получите 1 Toncoin на ваш счет"
    await message.answer(text=text, reply_markup=await referal_keyboards.referal_keyboard(user))