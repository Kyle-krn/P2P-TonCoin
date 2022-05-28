import aiohttp
import asyncio
from models import models
from tortoise import Tortoise, run_async
from data import config


async def get_currency(currency_name: str):
    url = "https://api.currencyapi.com/v3/latest"
    currency_token = "v1ZWvfDUkCHm4bnhuczYDRvC2ixrgGKIJfmBoMFG"
    params = {"apikey": currency_token}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            res = await resp.json()
    res = res['data']
    if currency_name not in res:
        return None
    else:
        return res[currency_name]


async def add_currency(currency_name: str):
    await Tortoise.init(config.TORTOISE_ORM)
    cur = await get_currency(currency_name=currency_name)
    if cur is None:
        return print("Валюта не найдена")
    cur_db = await models.Currency.get_or_none(name=cur['code'])
    if cur_db:
        return print("Валюта уже добавлена")
    await models.Currency.create(name=cur['code'], 
                                 exchange_rate=cur['value'],
                                 is_active=True)
    return print(f"Валюта {cur['code']} создана.")



async def lang_currency(currency_name: str, currency_ru: str, currency_eng: str):
    await Tortoise.init(config.TORTOISE_ORM)
    cur = await models.Currency.get(name=currency_name)
    print(cur.uuid)
    await models.Lang.create(target_table='lang', target_id=cur.uuid, rus=currency_ru, eng=currency_eng)



if __name__ == '__main__':
    run_async(lang_currency("EUR", "Евро", "Euro"))
    # run_async(add_currency("RUB"))
    