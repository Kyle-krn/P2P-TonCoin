from aiogram.dispatcher.filters.state import State, StatesGroup


class BuyState(StatesGroup):
    buy_amount = State()