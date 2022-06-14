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
    if message.text == "Кошелек":
        return await main_wallet_handler(message)
    elif message.text == "Продать Ton":
        return await sell_ton_handler(message)
    elif message.text == "Мои счета":
        return await payment_account_message_handler(message)
    elif message.text == "Купить Ton":
        return await buy_coin_hanlder(message)
    elif message.text == "Мои активные заказы":
        return await my_deals_handler(message)
    elif message.text == "Реферальная система":
        return await referal_handler(message)