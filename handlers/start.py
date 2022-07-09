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
        text = await models.Lang.get(uuid="ecc46c6b-90d1-45c3-be85-a3eace3b93f2")
        text = text.rus if user.lang == "ru" else text.eng
        # text = "Добро пожаловать в официальный бот для p2p обмена Toncoin.\n Выберите язык, на котором вам удобно работать:"
        return await message.answer(text=text, reply_markup=await keyboards.language_keyboard(user))
    else:
        text = await models.Lang.get(uuid="f82068f9-63c5-4c36-96b7-c5c5aa781a09")
        text = text.rus if user.lang == "ru" else text.eng
        # text = "Добро пожаловать!"

        await message.answer(text=text, reply_markup=await main_keyboard(user))

