from keyboards.inline import keyboards
from keyboards.reply.keyboards import main_keyboard
from loader import dp
from aiogram import types

from models import models
from utils.lang import lang_text



import requests
from data import config
import logging
import urllib.parse

@dp.message_handler(regexp="^(Язык: ru)$")
@dp.message_handler(regexp="^(Language: eng)$")
async def change_lang_handler(message: types.Message):
    user = await models.User.get(telegram_id=message.chat.id)
    text = await lang_text(lang_uuid="e0806c13-daba-4a79-a95e-97705c3090fb",
                           user=user)
    # text = "Добро пожаловать!"
    return await message.answer(text=text, reply_markup=await keyboards.language_keyboard(user))
    # await message.answer(text=text, reply_markup=await main_keyboard(user))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'lang')
async def set_lang(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    lang = call.data.split(':')[1]
    user.lang = lang
    await user.save()
    text = await lang_text(lang_uuid="f82068f9-63c5-4c36-96b7-c5c5aa781a09",
                           user=user)
    # text = "Добро пожаловать!"
    await call.message.delete()
    await call.message.answer(text=text, reply_markup=await main_keyboard(user))