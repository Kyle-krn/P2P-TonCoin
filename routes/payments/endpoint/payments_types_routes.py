import json
from typing import Union
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from loader import flash, templates
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
                                order_by: str = None):
    currencies = await models.Currency.exclude(name="TON")

    query = await query_filters(search)
    if search.data__json:
        uuid_list = await rowsql_get_distinct_list_value(search.data__json, table="user_payment_account_type")
        uuid_list = [i['uuid'] for i in uuid_list]
        query &= Q(uuid__in=uuid_list)

    payment_types = models.UserPaymentAccountType.filter(query)
    order_by, order_by_args = order_by_utils(order_by)
    payment_types = payment_types.order_by(*order_by_args)

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
        is_active = str_bool(form_list[indx+3][1])
        type = await models.UserPaymentAccountType.get(uuid=type_uuid)
        while "'" in data:
            data = data.replace("'", '"')
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = type.data
            flash(request, f"Invalid JSON - {data}", "danger")
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