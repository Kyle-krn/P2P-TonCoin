
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from loader import flash, manager
from models import models
from starlette import status
import utils.currency as currency_utils
from utils.utils import str_bool
from tortoise.exceptions import DoesNotExist
import utils.exceptions as custom_exc

post_currency_router = APIRouter()


@post_currency_router.post('/update_ton_rate', response_class=RedirectResponse)
async def update_ton(request: Request,
                     exchange_rate: float = Form(),
                     staff: models.Staff = Depends(manager)):
    ton_currency = await models.Currency.get(name="TON")
    ton_currency.exchange_rate = exchange_rate
    await ton_currency.save()
    flash(request, "Ton exchange rate update success", 'success')
    return RedirectResponse(
        request.url_for('get_currency'), 
        status_code=status.HTTP_302_FOUND)


@post_currency_router.post('/update_currency', response_class=RedirectResponse)
async def update_currency(request: Request,
                          staff: models.Staff = Depends(manager)):
    form_list = (await request.form())._list
    for indx in range(0, len(form_list), 5):
        currency_uuid = form_list[indx][1]
        rus_lang = form_list[indx+1][1] if form_list[indx+1][1] else None
        eng_lang = form_list[indx+2][1] if form_list[indx+2][1] else None
        exchange_rate = form_list[indx+3][1]
        is_active = str_bool(form_list[indx+4][1])
        currency = await models.Currency.get(uuid=UUID(currency_uuid))
        if rus_lang and eng_lang:
            lang_save = False
            cur_lang = await models.Lang.get_or_none(target_table="currency", target_id=currency_uuid)
            if cur_lang is None:
                cur_lang = models.Lang(target_table="currency", target_id=currency_uuid)
                lang_save = True
            
            if cur_lang.rus != rus_lang:
                cur_lang.rus = rus_lang
                lang_save = True
            if cur_lang.eng != eng_lang:
                cur_lang.eng = eng_lang
                lang_save = True
            if lang_save:
                await cur_lang.save()
        save = False
        if currency.exchange_rate != exchange_rate:
            currency.exchange_rate = float(exchange_rate)
            save = True
        if currency.is_active != is_active:
            currency.is_active = is_active
            save = True
        
        if save:
            await currency.save()
        
    return RedirectResponse(
        request.url_for('get_currency'), 
        status_code=status.HTTP_302_FOUND)


@post_currency_router.post('/add_currency', response_class=RedirectResponse)
async def update_currency(request: Request,
                          cur_name: str = Form(),
                          staff: models.Staff = Depends(manager)):
    exsists_currency = [i['name'] for i in await models.Currency.exclude(name="TON").values("name")]
    cur_list = [i.strip().upper() for i in cur_name.split(',') if i != '']
    error_exsists = []
    for cur in cur_list:
        if cur in exsists_currency:
            error_exsists.append(cur)
    cur_list = [i for i in cur_list if i not in error_exsists]
    success_cur_list, error_cur_list = await currency_utils.get_all_currency(currency=cur_list)
    if len(error_exsists) > 0:
        flash(request, f"Already exsists: {', '.join(error_exsists)}", "danger")
    if len(error_cur_list) > 0:
        flash(request, f"Not found: {', '.join(error_cur_list)}", "danger")
    
    for cur in success_cur_list:
        await models.Currency.create(name=cur['code'], 
                                    exchange_rate=cur['value'],
                                    is_active=False)
    if len(success_cur_list) > 0:
        flash(request, f"Success: {', '.join([i['code'] for i in success_cur_list])}", "success") # Здесь исправить
    return RedirectResponse(
        request.url_for('get_currency'), 
        status_code=status.HTTP_302_FOUND)



@post_currency_router.get('/delete_currency/{currency_uuid}', response_class=RedirectResponse)
async def delete_currency(request: Request,
                          currency_uuid: UUID,
                          ):
    try:
        currency = await models.Currency.get(uuid=currency_uuid)
        if currency.name == "TON":
            raise custom_exc.CurrencyTonDelete
        payments_account = await currency.user_payment_account_type.all()
        if len(payments_account) > 0:
            raise custom_exc.PaymentsAccountNotEmpty
        orders = await currency.orders.all()
        if len(orders) > 0:
            raise custom_exc.OrderNotEmpty 
        
        flash(request, f"{currency.name} deleted", "success")
        await currency.delete()
        
    except (DoesNotExist, custom_exc.PaymentsAccountNotEmpty) as exc:
        if isinstance(exc, DoesNotExist):
            flash(request, "Currency not found", "danger")
        elif isinstance(exc, custom_exc.PaymentsAccountNotEmpty):
            flash(request, "У валюты существуют платежные аккаунты", "danger")
        elif isinstance(exc, custom_exc.OrderNotEmpty):
            flash(request, "У валюты существуют заказы", "danger")
    
    return RedirectResponse(
        request.url_for('get_currency'), 
        status_code=status.HTTP_302_FOUND)

        




