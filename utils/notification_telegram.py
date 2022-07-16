import asyncio
from loader import bot
from models import models
from data import config
from aiogram import exceptions
import logging

# <a href="https://example.com">This is an example</a>
async def notification_new_user(user: models.User):
    text = f"Новый пользователь: <a href='{config.WEBHOOK_HOST}/user/{user.uuid}'>{user.tg_username if user.tg_username else 'Click'}</a>\n"
    referal_user = await user.referal_user
    if referal_user:
        text += f"Пригласивший пользователь: <a href='{config.WEBHOOK_HOST}/user/{referal_user.uuid}'>"  \
                f"{referal_user.tg_username if referal_user.tg_username else 'Click'}</a>\n\n"  \
                f"Реф. бонус: <a href='{config.WEBHOOK_HOST}/referal_children?user_id={referal_user.uuid}&invited_user_id={user.uuid}'>Click</a>"
    await bot.send_message(chat_id=config.NOTIFICATION_GROUP_ID, text=text)



async def notification_withdraw(withdraw: models.UserBalanceChange):
    user = await withdraw.user
    text = f"Пользователь <a href='{config.WEBHOOK_HOST}/user/{user.uuid}'>{user.tg_username if user.tg_username else user.telegram_id}</a> "  \
           f"запрашивает вывод на {withdraw.amount} TON\n\n"  \
           f"<a href='{config.WEBHOOK_HOST}/history_balance?uuid={withdraw.uuid}'>Click</a>"
    await bot.send_message(chat_id=config.NOTIFICATION_GROUP_ID, text=text)


async def notification_problem_order(order: models.Order):
    seller = await order.seller
    customer = await order.customer
    text = "<b>Необходимо решение администратора</b>\n\n"  \
           f"Проблемный заказ: <a href='{config.WEBHOOK_HOST}/order/{order.uuid}'>Click</a>\n"  \
           f"Продавец: <a href='{config.WEBHOOK_HOST}/user/{seller.uuid}'>{seller.tg_username if seller.tg_username else 'Click'}</a>\n"  \
           f"Покупатель: <a href='{config.WEBHOOK_HOST}/user/{customer.uuid}'>{customer.tg_username if customer.tg_username else 'Click'}</a>\n"
    await bot.send_message(chat_id=config.NOTIFICATION_GROUP_ID, text=text)



async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender
    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        logging.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        logging.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(rus_text: str, eng_text: str) -> int:
    """
    Simple broadcaster
    :return: Count of messages
    """
    count = 0
    users = await models.User.all()
    try:
        for user in users:
            text = rus_text if user.lang == "ru" else eng_text
            if await send_message(user.telegram_id, text):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count
