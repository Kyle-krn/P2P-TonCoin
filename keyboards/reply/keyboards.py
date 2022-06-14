from aiogram import types


async def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ref_button = types.KeyboardButton(text="Реферальная система")
    help_button = types.KeyboardButton(text="Схема Работы")
    wallet_button = types.KeyboardButton(text="Кошелек")
    sell_button = types.KeyboardButton(text="Продать Ton")
    buy_button = types.KeyboardButton(text="Купить Ton")
    bank_account_button = types.KeyboardButton(text="Мои счета")
    deals_button = types.KeyboardButton(text="Мои активные заказы")
    keyboard.add(wallet_button, sell_button)
    keyboard.add(bank_account_button, buy_button)
    keyboard.add(deals_button, ref_button)
    return keyboard