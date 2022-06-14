from aiogram.dispatcher.filters.state import State, StatesGroup


class WithdrawState(StatesGroup):
    amount = State()
    ton_wallet = State()