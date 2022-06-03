from aiogram import types

def referal_keyboard(user_uuid):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Отправь ссылку другу", url=f"https://t.me/share/url?url=https://t.me/TonCoinTestBot?start={user_uuid}"))
    return keyboard