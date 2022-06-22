import ast
from typing import Any, Union
from urllib.parse import urlencode
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Request
from loader import flash
from models import models
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status
from loader import templates, flash, manager
from tortoise.queryset import Q

from utils.currency import get_api_currency



currency_router = APIRouter()


@currency_router.get('/currency', response_class=HTMLResponse)
async def get_currency(request: Request):
    ton_currency = await models.Currency.get(name="TON")
    currencies = await models.Currency.all().exclude(name="TON").order_by('-created_at')
    context = {
                "request": request,
                "ton_currency": ton_currency,
                "currencies": currencies
                }
    return templates.TemplateResponse("currency.html", context)


@currency_router.post('/update_ton_rate', response_class=RedirectResponse)
async def update_ton(request: Request,
                     exchange_rate: float = Form()):
    ton_currency = await models.Currency.get(name="TON")
    ton_currency.exchange_rate = exchange_rate
    await ton_currency.save()
    flash(request, "Ton exchange rate update success", 'success')
    return RedirectResponse(
        "/currency", 
        status_code=status.HTTP_302_FOUND)


@currency_router.post('/update_currency', response_class=RedirectResponse)
async def update_currency(request: Request):
    form_list = (await request.form())._list
    for indx in range(0, len(form_list), 3):
        currency_uuid = form_list[indx][1]
        exchange_rate = form_list[indx+1][1]
        is_active = form_list[indx+2][1]
        if is_active == 'True':
            is_active = True
        else:
            is_active = False
        # delete = form_list[indx+3][1]

        currency = await models.Currency.get(uuid=UUID(currency_uuid))
        currency.exchange_rate = exchange_rate
        currency.is_active = is_active
        await currency.save()
        # if delete == 'True':
        #     await currency.delete()

    return RedirectResponse(
        "/currency", 
        status_code=status.HTTP_302_FOUND)


@currency_router.post('/add_currency', response_class=RedirectResponse)
async def update_currency(request: Request,
                          cur_name: str = Form()):
    cur = await get_api_currency(currency_name=cur_name)
    if cur is None:
        flash(request,"Not found currency", "danger")
    else:
        cur_db = await models.Currency.get_or_none(name=cur['code'])
        if cur_db:
            flash(request,"Currency already exists", "danger")
        else:
            await models.Currency.create(name=cur['code'], 
                                        exchange_rate=cur['value'],
                                        is_active=True)
            flash(request, "Success", "success")
    return RedirectResponse(
        "/currency", 
        status_code=status.HTTP_302_FOUND)
    # return print(f"Валюта {cur['code']} создана.")


    