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
from utils.pagination import pagination

currency_router = APIRouter()


@currency_router.get('/currency', response_class=HTMLResponse)
async def get_currency(request: Request,
                       name: str = None,
                       min_rate: Union[float, str] = None,
                       max_rate: Union[float, str] = None,
                       is_active: str = None,
                       min_created_at: str = None,
                       max_created_at: str = None,
                       order_by: str = None,
                       page: int = 1
                        ):
    if is_active == 'True':
        is_active = True
    elif is_active == 'False':
        is_active = False
    else:
        is_active = None
    
    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []
    print(order_by)
    ton_currency = await models.Currency.get(name="TON")
    search = {
        "name": None,
        "min_rate": None,
        "max_rate": None,
        "min_created_at": None,
        "max_created_at": None,
        "is_active": None,
    }
    
    query = Q()
    if name:
        query &= Q(name__icontains=name)
        search["name"] = name
    if min_rate:
        query &= Q(exchange_rate__gte=min_rate)
        search["min_rate"] = min_rate
    if max_rate:
        query &= Q(exchange_rate__lte=max_rate)
        search["max_rate"] = max_rate
    if is_active is not None:
        query &= Q(is_active=is_active)
        search["is_active"] = is_active
    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
        search["min_created_at"] = min_created_at
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)
        search["max_created_at"] = max_created_at

    currencies = models.Currency.filter(query).exclude(name="TON")

    

    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await currencies.count())
    currencies = currencies.offset(offset).limit(limit)
    
    if len(order_by) == 0:
        currencies = currencies.order_by("-created_at")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        currencies = currencies.order_by(*order_by)
    currencies = await currencies

    context = {
                "request": request,
                "ton_currency": ton_currency,
                "currencies": currencies,
                'search': search,
                'params': request.query_params._dict,
                'order_by': order_by,
                "page": page,
                "last_page": last_page,
                "previous_page": previous_page,
                "next_page": next_page,
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
    exsists_currency = [i['name'] for i in await models.Currency.exclude(name="TON").values("name")]
    cur_list = [i.strip().upper() for i in cur_name.split(',') if i != '']
    error_exsists = []
    for cur in cur_list:
        if cur in exsists_currency:
            error_exsists.append(cur)
    cur_list = [i for i in cur_list if i not in error_exsists]
    success_cur_list, error_cur_list = await get_api_currency(currency=cur_list)
    if len(error_exsists) > 0:
        flash(request, f"Already exsists: {', '.join(error_exsists)}", "danger")
    if len(error_cur_list) > 0:
        flash(request, f"Not found: {', '.join(error_cur_list)}", "danger")
    
    for cur in success_cur_list:
        await models.Currency.create(name=cur['code'], 
                                    exchange_rate=cur['value'],
                                    is_active=False)
    if len(success_cur_list) > 0:
        flash(request, f"Success: {', '.join(success_cur_list)}", "success")
    # if cur is None:
    #     flash(request,"Not found currency", "danger")
    # else:
    #     cur_db = await models.Currency.get_or_none(name=cur['code'])
    #     if cur_db:
    #         flash(request,"Currency already exists", "danger")
    #     else:
    #         await models.Currency.create(name=cur['code'], 
    #                                     exchange_rate=cur['value'],
    #                                     is_active=True)
    #         flash(request, "Success", "success")
    return RedirectResponse(
        "/currency", 
        status_code=status.HTTP_302_FOUND)
    # return print(f"Валюта {cur['code']} создана.")



# @currency_router.get("/currency_sort/{column}", response_class=RedirectResponse)
# async def sort_user(request: Request,
#                     column: str,
#                     staff: models.Staff = Depends(manager)):
#     params = request.query_params._dict
#     if "order_by" not in params:
#         if column[0] != "~":
#             params['order_by'] = [column]
#     else:
#         params['order_by'] = ast.literal_eval(params['order_by'])
#         column_name = column[1:] 
        
#         if column[0] == "~" and len([i for i in params["order_by"] if column_name == i[1:]]) > 0:
#             params["order_by"] = [i for i in params["order_by"] if column_name != i[1:]]
#         elif column[0] != "~":
#             params["order_by"] = [i for i in params["order_by"] if column_name != i[1:]]
#             params["order_by"].append(column)
#     return "/currency?" + urlencode(params)