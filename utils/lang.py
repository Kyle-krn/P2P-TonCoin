from models import models

async def lang_currency(currency:models.Currency):
    '''Возвращает имя валюты'''
    cur_name = currency.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
    if lang_cur:
        cur_name = lang_cur.rus
    return cur_name

async def lang_payment_type(payment_type: models.UserPaymentAccountType):
    '''Возвращает имя типа платежки'''
    name = payment_type.name
    lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=payment_type.uuid)
    if lang_type:
        name = lang_type.rus
    return name