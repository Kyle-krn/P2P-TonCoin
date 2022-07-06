from uuid import UUID
from models import models


async def lang_currency(currency:models.Currency, user: models.User):
    '''Возвращает имя валюты'''
    cur_name = currency.name
    lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=currency.uuid)
    if lang_cur:
        cur_name = lang_cur.rus if user.lang == 'ru' else lang_cur.eng
    return cur_name


async def lang_payment_type(payment_type: models.UserPaymentAccountType, user: models.User):
    '''Возвращает имя типа платежки'''
    name = payment_type.name
    lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=payment_type.uuid)
    if lang_type:
        name = lang_type.rus if user.lang == 'ru' else lang_type.eng
    return name


async def lang_text(lang_uuid: UUID, 
                    user: models.User, 
                    format: dict = None):
    text = await models.Lang.get(uuid=lang_uuid)
    text = text.rus if user.lang == 'ru' else text.eng
    if format:
        text = text.format(**format)
    return text