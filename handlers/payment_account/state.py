from aiogram.dispatcher.filters.state import State, StatesGroup


class PaymentAccountState(StatesGroup):
    data = State()