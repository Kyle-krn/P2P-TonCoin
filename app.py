from aiogram import executor
# from handlers.wallet.main_wallet import init_message_filter

from loader import dp, db
from data.config import TORTOISE_ORM
import middlewares, filters, handlers 
# from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    await db.init(config=TORTOISE_ORM)
    # await init_message_filter()
    # await db.generate_schemas()
    # Уведомляет про запуск
    # await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)

