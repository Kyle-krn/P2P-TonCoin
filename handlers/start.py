import uuid
from loader import dp
from aiogram import types
from models import models
from keyboards.inline import keyboards
from keyboards.reply.keyboards import main_keyboard


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = await models.User.get_or_none(telegram_id=message.chat.id)
    if not user:
        lang = message.from_user.locale
        user_kwargs = {
            "telegram_id": message.chat.id,
            "tg_username": message.chat.username,
            "lang": lang
        }
        parent_referal = None
        if " " in message.text:
            parent_referal_uuid = message.text.split(' ')[1]
            parent_referal = await models.User.get_or_none(uuid=parent_referal_uuid)
            if parent_referal:
                user_kwargs["referal_user_id"] = parent_referal.uuid
        user = await models.User.create(**user_kwargs)
        if parent_referal:
            await models.UserReferalBonus.create(user=parent_referal,
                                                 invited_user=user,
                                                 state="created")
        text = "Добро пожаловать в официальный бот для p2p обмена Toncoin.\n"  \
            "Выберите язык, на котором вам удобно работать:"
        return await message.answer(text=text, reply_markup=await keyboards.language_keyboard())
    else:
        text = "Добро пожаловать!"
        await message.answer(text=text, reply_markup=await main_keyboard())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'lang')
async def set_lang(call: types.CallbackQuery):
    user = await models.User.get(telegram_id=call.message.chat.id)
    lang = call.data.split(':')[1]
    user.lang = lang
    await user.save()
    text = "Добро пожаловать!"
    await call.message.answer(text=text, reply_markup=await main_keyboard())