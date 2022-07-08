import asyncio
import aiohttp

async def validate_wallet(wallet_address):
    url = "https://toncenter.com/api/v2/getWalletInformation"
    params = {"address": wallet_address}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            res = await resp.json()
            return res


# async def get_currency_ton():
#     # ?ids=the-open-network&vs_currencies=usd
#     url = "https://api.coingecko.com/api/v3/simple/price"
#     params = {'ids': "the-open-network", "vs_currencies": "usd"}
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url=url, params=params) as resp:
#             res = await resp.json()
#             return res['the-open-network']['usd']

