from loader import dp
from aiogram import types
from models import models
from keyboards.inline import keyboards

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await models.User.get_or_create(telegram_id=message.chat.id)
    text = "Добро пожаловать в официальный бот для p2p обмена Toncoin.\n"  \
           "Выберите язык, на котором вам удобно работать:"
    return await message.answer(text=text, reply_markup=await keyboards.language_keyboard())

