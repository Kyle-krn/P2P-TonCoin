from uuid import UUID
import aiohttp
from models import models
from tortoise import Tortoise, run_async
from data import config
from tortoise.queryset import Q
from utils.currency import get_currency_ton

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


async def add_payment_type(pay_name: str, cur_name: str, pay_dict: dict):
    await Tortoise.init(config.TORTOISE_ORM)
    # print(up.__dict__)
    cur = await models.Currency.get_or_none(name=cur_name)
    if cur is None or cur.name == "TON":
        print("Валюта не найдена или вы пытаетесь добавить TON")
        return 
    await models.UserPaymentAccountType.create(name=pay_name, data=pay_dict, currency=cur, is_active=True)


async def insert_lang():
    await Tortoise.init(config.TORTOISE_ORM)
    # text = "Введите {payment_type_data_value}:"
    text = "Выберите способы оплаты, которые доступны для этого заказа, или создайте новый"
    
    await models.Lang.create(rus=text, eng=text)

async def test_json_field():
    await Tortoise.init(config.TORTOISE_ORM)
    payment = await models.UserPaymentAccountType.filter(Q(data__icontains="email"))
    print(payment)

async def test_api_key():
    await Tortoise.init(config.TORTOISE_ORM)
    p = await models.CurrencyApiKey.get(is_active=True)
    print(p.is_active)

if __name__ == '__main__':
    # test()
    run_async(test_api_key())
    # run_async(lang_currency("EUR", "Евро", "Euro"))
    # run_async(add_currency("UAH"))
    # run_async(add_payment_type(pay_name="СберБанк", cur_name="RUB", pay_dict={"Номер ЛК": "", "email": "", "Номер телефона": ""}))
    
    # run_async(add_ton_currency())
    # run_async(get_serial_int())
    # run_async(add_payment_type())
    # run_async(get_acc_test())