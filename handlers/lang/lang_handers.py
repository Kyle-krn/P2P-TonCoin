from keyboards.inline import keyboards
from keyboards.reply.keyboards import main_keyboard
from loader import dp
from aiogram import types

from models import models


@dp.message_handler(regexp="^(Язык: ru)$")
@dp.message_handler(regexp="^(Language: eng)$")
async def change_lang_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = await models.Lang.get(uuid="e0806c13-daba-4a79-a95e-97705c3090fb")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Добро пожаловать!"
    return await message.answer(text=text, reply_markup=await keyboards.language_keyboard(user))
    # await message.answer(text=text, reply_markup=await main_keyboard(user))




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'lang')
async def set_lang(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    lang = call.data.split(':')[1]
    user.lang = lang
    await user.save()
    text = await models.Lang.get(uuid="f82068f9-63c5-4c36-96b7-c5c5aa781a09")
    text = text.rus if user.lang == "ru" else text.eng
    # text = "Добро пожаловать!"
    await call.message.delete()
    await call.message.answer(text=text, reply_markup=await main_keyboard(user))