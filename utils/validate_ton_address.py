import asyncio
import aiohttp

async def validate_wallet(wallet_address):
    url = "https://toncenter.com/api/v2/getWalletInformation"
    params = {"address": wallet_address}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as resp:
            res = await resp.json()
            return res


