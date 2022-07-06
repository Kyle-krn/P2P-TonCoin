from aiogram import executor
from loader import dp, db
from data.config import TORTOISE_ORM
import middlewares, filters, handlers 
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    await db.init(config=TORTOISE_ORM)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

