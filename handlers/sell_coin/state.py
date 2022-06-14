from aiogram.dispatcher.filters.state import State, StatesGroup


class SellTonState(StatesGroup):
    amount = State()
    fee = State()
    currency = State()
    min_buy_sum = State()
    pay_acc_data = State()