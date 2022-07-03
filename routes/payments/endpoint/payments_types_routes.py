import json
from typing import Union
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from loader import flash, templates, manager
from models import models
from tortoise.queryset import Q
import starlette.status as status
from utils.models_utils import query_filters
from utils.order_by import order_by_utils
from utils.search_db_json import rowsql_get_distinct_list_value
from utils.utils import str_bool
from ..pydantic_models import PaymentsTypeSearch

payments_type_router = APIRouter()


@payments_type_router.get("/payments_account_type", response_class=HTMLResponse)
async def payments_account_type(request: Request,
                                search: PaymentsTypeSearch = Depends(PaymentsTypeSearch),
                                order_by: str = None,
                                staff: models.Staff = Depends(manager)):
    currencies = await models.Currency.exclude(name="TON")
    query = await query_filters(search)
    if search.data__json:
        uuid_list = await rowsql_get_distinct_list_value(search.data__json, table="user_payment_account_type")
        uuid_list = [i['uuid'] for i in uuid_list]
        query &= Q(uuid__in=uuid_list)

    payment_types = models.UserPaymentAccountType.filter(query)
    order_by, order_by_args = order_by_utils(order_by)
    payment_types = payment_types.order_by(*order_by_args)

    payment_types = await payment_types.prefetch_related("currency")
    

    for pay_type in payment_types:
        lang_type = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=pay_type.uuid)
        pay_type.rus = lang_type.rus if lang_type else None
        pay_type.eng = lang_type.eng if lang_type else None

    context = {"request": request,
               "payment_types": payment_types,
               "currencies": currencies,
               "search": search,
               "params": request.query_params._dict,
               "order_by": order_by}
               
    return templates.TemplateResponse("payment_types.html", context)


@payments_type_router.post("/update_payment_types", response_class=HTMLResponse)
async def update_payment_types(request: Request,
                               staff: models.Staff = Depends(manager)):
    form_list = (await request.form())._list
    for indx in range(0, len(form_list), 7):
        type_uuid = UUID(form_list[indx][1])
        currency_uuid = UUID(form_list[indx+1][1])
        name = form_list[indx+2][1]
        rus_lang = form_list[indx+3][1]
        eng_lang = form_list[indx+4][1]
        
        
        data = form_list[indx+5][1]
        is_active = str_bool(form_list[indx+6][1])
        type = await models.UserPaymentAccountType.get(uuid=type_uuid)
        while "'" in data:
            data = data.replace("'", '"')
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = type.data
            flash(request, f"Invalid JSON - {data}", "danger")

        if rus_lang and eng_lang:
            lang_save = False
            pay_type_lang = await models.Lang.get_or_none(target_table="user_payment_account_type", target_id=type_uuid)
            if pay_type_lang is None:
                pay_type_lang = models.Lang(target_table="user_payment_account_type", target_id=type_uuid)
                lang_save = True
            
            if pay_type_lang.rus != rus_lang:
                pay_type_lang.rus = rus_lang
                lang_save = True
            if pay_type_lang.eng != eng_lang:
                pay_type_lang.eng = eng_lang
                lang_save = True
            if lang_save:
                await pay_type_lang.save()


        save = False
        if type.currency_id != currency_uuid:
            type.currency_id = currency_uuid
            save = True
        if type.name != name:
            type.name = name
            save = True

        if type.data != json_data:
            type.data = json_data
            save = True
        if type.is_active != is_active:
            type.is_active = is_active
            save = True
        
        if save:
            await type.save()

    params = request.query_params
    if params != "":
        params = "?" + str(params)
    
    return RedirectResponse(
        request.url_for('payments_account_type') + params, 
        status_code=status.HTTP_302_FOUND) 




# @payments_type_router.get("/sort/payments_account_type/{column}", response_class=RedirectResponse)
# async def sort_user(request: Request,
#                     column: str,
#                     user_uuid: UUID = None,
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
#     redirect_url = request.url.path.split('/')[2]
#     return f'/{redirect_url}?' + urlencode(params)