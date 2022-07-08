import asyncio
import aiohttp
import aioschedule
from models import models
import utils.currency as currency_utils
# from utils.currency import get_api_currency

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
    print("currency update")

async def scheduler():
    aioschedule.every().day.at("00:01").do(update_currency_ton)
    aioschedule.every().day.at("00:00").do(update_rate_currency)
    # aioschedule.do(update_likes)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)