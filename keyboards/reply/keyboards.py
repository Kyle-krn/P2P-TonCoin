from aiogram import types


async def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ref_button = types.KeyboardButton(text="Реферальная система")
    help_button = types.KeyboardButton(text="Схема Работы")
    wallet_button = types.KeyboardButton(text="Кошелек")
    sell_button = types.KeyboardButton(text="Продать Ton")
    buy_button = types.KeyboardButton(text="Купить Ton")
    bank_account_button = types.KeyboardButton(text="Мои счета")
    keyboard.add(wallet_button, sell_button)
    keyboard.add(bank_account_button, buy_button)
    return keyboard