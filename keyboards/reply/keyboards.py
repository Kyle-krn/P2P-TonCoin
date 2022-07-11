from aiogram import types
from models import models


async def main_keyboard(user: models.User):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

    keyboard.add(types.KeyboardButton(text="Кошелек" if user.lang == 'ru' else 'Wallet'),
                 types.KeyboardButton(text="Продать Ton" if user.lang == 'ru' else 'Sell Ton'),
                 types.KeyboardButton(text="Купить Ton" if user.lang == 'ru' else 'Buy Ton'),
                 types.KeyboardButton(text="Мои счета" if user.lang == 'ru' else 'My bank account'),
                 types.KeyboardButton(text="Мои активные заказы" if user.lang == 'ru' else 'My active deals'),
                 
                 types.KeyboardButton(text="Реферальная система" if user.lang == 'ru' else "Referal system"),
                 types.KeyboardButton(text="Схема работы" if user.lang == 'ru' else 'Scheme of work'),
                 
                 types.KeyboardButton(text="Язык: ru" if user.lang == 'ru' else 'Language: eng')
                 )

    # text = "Реферальная система" if user.lang == 'ru' else "Referal system"
    ref_button = types.KeyboardButton(text="Реферальная система" if user.lang == 'ru' else "Referal system")
    help_button = types.KeyboardButton(text="Схема работы" if user.lang == 'ru' else 'Scheme of work')
    wallet_button = types.KeyboardButton(text="Кошелек" if user.lang == 'ru' else 'Wallet')
    sell_button = types.KeyboardButton(text="Продать Ton" if user.lang == 'ru' else 'Sell Ton')
    buy_button = types.KeyboardButton(text="Купить Ton" if user.lang == 'ru' else 'Buy Ton')
    bank_account_button = types.KeyboardButton(text="Мои счета" if user.lang == 'ru' else 'My bank account')
    deals_button = types.KeyboardButton(text="Мои активные заказы" if user.lang == 'ru' else 'My active deals')
    lang_button = types.KeyboardButton(text="Язык: ru" if user.lang == 'ru' else 'Language: eng')
    return keyboard