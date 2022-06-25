import ast
import json
from typing import Union
from urllib.parse import urlencode
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from tortoise.exceptions import DoesNotExist
from loader import flash, manager, templates
from models import models
from tortoise.queryset import Q
import starlette.status as status
from utils.pagination import pagination
from utils.search_db_json import rowsql_get_distinct_list_value


payments_type_router = APIRouter()


@payments_type_router.get("/payments_account_type", response_class=HTMLResponse)
async def payments_account_type(request: Request,
                                name: str = None,
                                payment_data: str = None,
                                currency_uuid: Union[UUID,str] = None,
                                is_active: Union[bool,str] = None,
                                min_created_at: str = None,
                                max_created_at: str = None,
                                order_by: str = None):
    currencies = await models.Currency.exclude(name="TON")
    
    if isinstance(is_active, str):
        is_active = None
    if isinstance(currency_uuid, str):
        currency_uuid = None

    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []
    
    search = {
        "name": None,
        "payment_data": None,
        "currency_uuid": None,
        "is_active": None,
        "min_created_at": None, 
        "max_created_at": None 
    }
    query = Q()
    if name:
        query &= Q(name__icontains=name)
        search['name'] = name
    if currency_uuid:
        query &= Q(currency_id=currency_uuid)
        search['currency_uuid'] = currency_uuid
    if is_active is not None:
        query &= Q(is_active=is_active)
        search['is_active'] = is_active
    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
        search["min_created_at"] = min_created_at
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)
        search["max_created_at"] = max_created_at
    if payment_data:
        uuid_list = await rowsql_get_distinct_list_value(payment_data, table="user_payment_account_type")
        print(uuid_list)
        uuid_list = [i['uuid'] for i in uuid_list]
        query = query & Q(uuid__in=uuid_list)

    payment_types = models.UserPaymentAccountType.filter(query)
    
    if len(order_by) == 0:
        payment_types = payment_types.order_by("-created_at", "uuid")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        payment_types = payment_types.order_by(*order_by)
    payment_types = payment_types.prefetch_related("currency")
    context = {"request": request,
               "payment_types": await payment_types,
               "currencies": currencies,
               "search": search,
               "params": request.query_params._dict,
               "order_by": order_by}
    return templates.TemplateResponse("payment_types.html", context)
    

@payments_type_router.post("/update_payment_types", response_class=HTMLResponse)
async def update_payment_types(request: Request):
    form_list = (await request.form())._list
    for indx in range(0, len(form_list), 4):
        type_uuid = form_list[indx][1]
        currency_uuid = form_list[indx+1][1]
        data = form_list[indx+2][1]
        is_active = form_list[indx+3][1]
        type = await models.UserPaymentAccountType.get(uuid=type_uuid)
        while "'" in data:
            data = data.replace("'", '"')
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = type.data
            flash(request, f"Invalid JSON - {data}", "danger")
        if is_active == 'True':
            is_active = True
        else:
            is_active = False
        type.update_from_dict({'currency_id': UUID(currency_uuid),
                                        'data': json_data,
                                        'type_id': type_uuid,
                                        'is_active': is_active
                                        })
        await type.save()
        flash(request, "Success", "success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    
    return RedirectResponse(
        '/payments_account_type' + params, 
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