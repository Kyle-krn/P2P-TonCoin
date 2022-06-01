from loader import dp
from aiogram import types
from aiogram.dispatcher import FSMContext

@dp.callback_query_handler(lambda call: call.data == 'stop_state', state="*")
async def cancel_state_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Отмена")