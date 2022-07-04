from handlers.lang.lang_handers import change_lang_handler
from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from handlers.wallet.main_wallet import main_wallet_handler
from handlers.sell_coin.sell_coin_handlers import sell_ton_handler
from handlers.payment_account.payment_account_handlers import payment_account_message_handler
from handlers.buy_coin.buy_coin_handlers import buy_coin_hanlder
from handlers.deals.deals_handlers import my_deals_handler
from handlers.referal.referal_handlers import referal_handler


@dp.callback_query_handler(lambda call: call.data == 'stop_state', state="*")
async def cancel_state_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Отмена")


async def cancel_state_message(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text in ("Кошелек", "Wallet"):
        return await main_wallet_handler(message)
    elif message.text in ("Продать Ton", "Sell Ton"):
        return await sell_ton_handler(message)
    elif message.text in ("Мои счета", "My bank account"):
        return await payment_account_message_handler(message)
    elif message.text in ("Купить Ton", "Buy Ton"):
        return await buy_coin_hanlder(message)
    elif message.text in ("Мои активные заказы", "My active deals"):
        return await my_deals_handler(message)
    elif message.text in ("Реферальная система", "Referal system"):
        return await referal_handler(message)
    elif message.text in ("Язык: ru", "Language: eng"):
        return await change_lang_handler(message)