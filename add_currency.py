from uuid import UUID
import aiohttp
import asyncio
from models import models
from tortoise import Tortoise, run_async
from data import config
from tortoise.queryset import Q
from utils.validate_ton_address import get_currency_ton
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


async def add_ton_currency():
    await Tortoise.init(config.TORTOISE_ORM)
    ton_cur = await get_currency_ton()
    await models.Currency.create(name='TON',
                                 exchange_rate=ton_cur,
                                 is_active=True)

async def lang_currency(currency_name: str, currency_ru: str, currency_eng: str):
    await Tortoise.init(config.TORTOISE_ORM)
    cur = await models.Currency.get(name=currency_name)
    print(cur.uuid)
    await models.Lang.create(target_table='lang', target_id=cur.uuid, rus=currency_ru, eng=currency_eng)


async def add_payment_type():
    await Tortoise.init(config.TORTOISE_ORM)
    # up = await models.UserPaymentAccountType.get(name="Тинькофф")
    # print(up.__dict__)
    cur = await models.Currency.get(name="EUR")
    await models.UserPaymentAccountType.create(name="EuroBank", data={"Номер dog": ""}, currency=cur, is_active=True)

async def get_serial_int(table_name: str, uuid: UUID):
    await Tortoise.init(config.TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    sql = f"select serial_int from {table_name} where uuid = {uuid}"
    query = await conn.execute_query_dict(sql)
    return query

async def get_acc_test():
    await Tortoise.init(config.TORTOISE_ORM)
    user = await models.User.get(telegram_id=5039078302)
    user_payment_accounts = await models.UserPaymentAccount.filter(Q(user=user) & Q(type__currency__name="RUB"))

async def test_children_order():
    # 
    await Tortoise.init(config.TORTOISE_ORM)
    order = await models.Order.get(uuid="1be5defc-0c52-4d34-bc05-cb95247ab4a5")
    parent = await order.parent
    order_user_payment_account = await parent.order_user_payment_account.filter(account__type__uuid="20bca4c0-c4c6-4e1b-b06e-2db18e10fedc")
    print((await order_user_payment_account[0].account).data)


async def insert_lang():
    await Tortoise.init(config.TORTOISE_ORM)
    text = "Продавец сообщил, что не получил оплату от вас."  \
           "Пришлите, пожалуйста, подтверждение оплаты (чек)"  \
           "в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение."  \
           "Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен"
    await models.Lang.create(rus=text, eng=text)


def test():
    text = "Это текст"
    print(text.format(test="hui"))

if __name__ == '__main__':
    # test()
    run_async(insert_lang())
    # run_async(lang_currency("EUR", "Евро", "Euro"))
    # run_async(add_currency("RUB"))
    # run_async(get_serial_int())
    # run_async(add_payment_type())
    # run_async(get_acc_test())