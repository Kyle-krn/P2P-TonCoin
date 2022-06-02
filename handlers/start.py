from loader import dp
from aiogram import types
from models import models
from keyboards.inline import keyboards
from keyboards.reply.keyboards import main_keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    print(message.text)
    user = await models.User.get_or_none(telegram_id=message.chat.id)
    if not user:
        lang = message.from_user.locale
        await models.User.create(telegram_id=message.chat.id, 
                                 tg_username=message.chat.username,
                                 lang=lang,
                                 )
    
    text = "Добро пожаловать в официальный бот для p2p обмена Toncoin.\n"  \
           "Выберите язык, на котором вам удобно работать:"
    return await message.answer(text=text, reply_markup=await keyboards.language_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'lang')
async def set_lang(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    lang = call.data.split(':')[1]
    user.lang = lang
    await user.save()
    text = "Добро пожаловать!"
    await call.message.answer(text=text, reply_markup=await main_keyboard())
    
