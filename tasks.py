import asyncio
import aiohttp
import aioschedule
from handlers.buy_coin.buy_coin_handlers import cancel_buy_order_handler
from models import models
import utils.currency as currency_utils
from datetime import datetime, timedelta
async def update_currency_ton():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': "the-open-network", "vs_currencies": "usd"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            res = await resp.json()
            ton_rate = res['the-open-network']['usd']    
    ton_bd = await models.Currency.get(name='TON')
    ton_bd.exchange_rate = ton_rate
    await ton_bd.save()


async def update_rate_currency():
    rate_list = await models.Currency.exclude(name="TON").values("name")
    rate_list = [i['name'] for i in rate_list]
    new_rate, _ = await currency_utils.get_all_currency(rate_list)
    for rate in new_rate:
        cur = await models.Currency.get(name=rate['code'])
        cur.exchange_rate = rate['value']
        await cur.save()


async def wait_buyer_send_funds_order_check():
    orders = await models.Order.filter(state="wait_buyer_send_funds")
    for order in orders:
        if (order.updated_at + timedelta(minutes=15)).replace(tzinfo=None) < datetime.utcnow():
            await cancel_buy_order_handler(order_uuid=order.uuid)

async def scheduler():
    aioschedule.every().minute.do(update_currency_ton)
    aioschedule.every().minute.do(wait_buyer_send_funds_order_check)
    aioschedule.every().hour.do(update_rate_currency)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)