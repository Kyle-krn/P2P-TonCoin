from typing import List
import aiohttp
from models import models

async def get_all_currency(currency: List[str]):
    url = "https://api.currencyapi.com/v3/latest"
    currency_token = "v1ZWvfDUkCHm4bnhuczYDRvC2ixrgGKIJfmBoMFG"
    params = {"apikey": currency_token}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            res = await resp.json()
    res = res['data']
    success_cur_list = []
    error_cur_list = []
    for cur in currency:
        if cur in res:
            success_cur_list.append(res[cur])
        else:
            error_cur_list.append(cur)
    return success_cur_list, error_cur_list


async def get_currency_ton():
    # ?ids=the-open-network&vs_currencies=usd
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': "the-open-network", "vs_currencies": "usd"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            res = await resp.json()
            return res['the-open-network']['usd']