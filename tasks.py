import asyncio
import aiohttp
import aioschedule
from handlers.buy_coin.buy_coin_handlers import cancel_buy_order_handler
from models import models
import utils.currency as currency_utils
from datetime import datetime, timedelta
from loader import bot
from utils.lang import lang_text

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


async def problem_seller_no_funds_order_check():
    orders = await models.Order.filter(state="problem_seller_no_funds")
    for order in orders:
        if (order.updated_at + timedelta(hours=24)).replace(tzinfo=None) < datetime.utcnow():
            await cancel_buy_order_handler(order_uuid=order.uuid)


async def check_main_ton_wallet():
    params = {"address": "EQDcYqGh0d6i_kogT4QXvTuEq_iu61qPrZDVhbGnDvdrk-f3",
            "limit": 20}
    response = None
    for i in range(5):
        async with aiohttp.ClientSession() as session:
            async with session.get(url="https://toncenter.com/api/v2/getTransactions", params=params) as resp:
                if resp.status != 200:
                    await asyncio.sleep(1)
                    continue
                else:
                    response = await resp.json()
                    break
    if response is None:
        return
    if response['ok'] is True:
        transactions = response['result']
        for transaction in transactions:
            if transaction['transaction_id']['hash'] == "KfOUWLY6Hj80BjW533q8WOeABF1JumhlRU1Ua32ABJo=":
                return
            if transaction['in_msg']['value'] == '0':
                continue
            
            amount = int(transaction['in_msg']['value']) / 1000000000
            hash = transaction['transaction_id']['hash']
            wallet = transaction['in_msg']['source']
            code = transaction['in_msg']['message']

            existing_transaction = await models.UserBalanceChange.get_or_none(hash=hash)
            if existing_transaction:
                continue

            user_balance_change = None
            if code != '':
                user_balance_change = await models.UserBalanceChange.get_or_none(code=code)
            
            if user_balance_change is not None:
                user = await user_balance_change.user
                user_balance_change.amount = amount
                user_balance_change.state = "done"
                user_balance_change.hash = hash
                user_balance_change.wallet = wallet
                user.balance += amount
                await user_balance_change.save()
                await user.save()
                
                lang = await lang_text(lang_uuid="201f04fa-64ca-40bc-a3b2-31804a73c540", user=user, format={"amount": str(amount)})
                try:
                    await bot.send_message(chat_id=user.telegram_id, text=lang)
                except:
                    pass
            else:
                await models.UserBalanceChange.create(user=None,
                                                     type="topup",
                                                     amount=amount,
                                                     hash=hash,
                                                     wallet=wallet,
                                                     code=code,
                                                     state="done")

async def scheduler():
    aioschedule.every().minute.do(update_currency_ton)
    aioschedule.every().minute.do(wait_buyer_send_funds_order_check)
    aioschedule.every().minute.do(check_main_ton_wallet)
    aioschedule.every().hour.do(update_rate_currency)
    aioschedule.every().hour.do(problem_seller_no_funds_order_check)
    while True:
        await aioschedule.run_pending() 
        await asyncio.sleep(1)