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

payment_account_router = APIRouter()

@payment_account_router.get('/user_payments_account/{uuid}')
@payment_account_router.get('/payments_account')
async def user_payment_account(request: Request,
                               uuid: UUID = None,
                               user_uuid: Union[UUID,str] = None,
                               type_uuid: Union[UUID,str] = None,
                               currency_uuid: Union[UUID,str] = None,
                               payment_data: str = None,
                               is_active: Union[bool,str] = None,
                               min_updated_at: str = None,
                               max_updated_at: str = None,
                               min_created_at: str = None,
                               max_created_at: str = None,
                               order_by: str = None,
                               page:int = 1):
    
    if user_uuid is not None and (isinstance(user_uuid, UUID) is False or (await models.User.get_or_none(uuid=user_uuid)) is None):
        user_uuid = None
        flash(request, "Error Parent UUID")
    
    if uuid:
        user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
        query = Q(user=user)
    else:
        user = None
        query = Q()

    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []
    
    # user = await models.User.get(uuid=uuid)

    if isinstance(is_active, str):
        is_active = None
    if isinstance(type_uuid, str):
        type_uuid = None
    if isinstance(currency_uuid, str):
        currency_uuid = None

    # selected_type = await models.UserPaymentAccountType.get(name="Тинькоф")
    search = {
        'type_uuid': None,
        'currency_uuid': None,
        'is_active': None,
        'min_updated_at': None,
        'max_updated_at': None,
        'min_created_at': None,
        'max_created_at': None,
        'user_uuid': None
    }
    payments_account = models.UserPaymentAccount.filter(query)
    
    # query = Q()

    if user_uuid:
        query = Q(user_id=user_uuid)
        search['user_uuid'] = user_uuid

    if type_uuid:
        query &= Q(type_id=type_uuid)
        search['type_uuid'] = type_uuid
    if currency_uuid:
        query &= Q(type__currency_id=currency_uuid)
        search['currency_uuid'] = currency_uuid
    if is_active is not None:
        query = query & Q(is_active=is_active)
        search["is_active"] = is_active

    if min_updated_at:
        query = query & Q(created_at__gte=min_updated_at)
        search["min_updated_at"] = min_updated_at
    if max_updated_at:
        query = query & Q(created_at__lte=max_updated_at)
        search["max_updated_at"] = max_updated_at
    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
        search["min_created_at"] = min_created_at
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)
        search["max_created_at"] = max_created_at

    if payment_data:
        uuid_list = await rowsql_get_distinct_list_value(payment_data, table="user_payment_account")
        uuid_list = [i['uuid'] for i in uuid_list]
        query = query & Q(uuid__in=uuid_list)
    payments_account = payments_account.filter(query)

    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await payments_account.count())
    payments_account = payments_account.offset(offset).limit(limit)
    
    currency = await models.Currency.exclude(name="TON")
    payments_type = await models.UserPaymentAccountType.filter().prefetch_related("currency")


    if len(order_by) == 0:
        payments_account = payments_account.order_by("-created_at", "uuid")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        payments_account = payments_account.order_by(*order_by)
        
    payments_account = await payments_account.prefetch_related("type__currency", "user")

    context = {
        'request': request,
        'user': user,
        'params': request.query_params._dict,
        'payments_account': payments_account,
        'payments_type': payments_type,
        'currency': currency,
        'search': search,
        'order_by': order_by,
        "page": page,
        "last_page": last_page,
        "previous_page": previous_page,
        "next_page": next_page,
        "pagination_url": f"/user_payments_account/{user.uuid}" if user else "/payments_account"
    }

    template_name = "users/user_payment_account.html" if user else "/payments_account.html"
    return templates.TemplateResponse(template_name, context)



@payment_account_router.post('/create_payments_account')
async def create_payments_account(request: Request,
                                  redirect_uuid: UUID = Form(None),
                                  user_uuid: UUID = Form(),
                                  type_uuid: UUID = Form(),
                                  data: str = Form(),
                                  is_active: bool = Form(False)):
    try:
        user = await models.User.get(uuid=user_uuid)
        while "'" in data:
            data = data.replace("'", '"')
        json_data = json.loads(data)
    except (json.decoder.JSONDecodeError, DoesNotExist) as exc:
        if isinstance(exc,json.decoder.JSONDecodeError):
            flash(request, f"Invalid JSON: {data}", 'danger')
        else:
            flash(request, f"Not found user: {user_uuid}", 'danger')
    else:
        await models.UserPaymentAccount.create(user=user, 
                                               type_id=type_uuid, 
                                               data=data, 
                                               is_active=is_active)
        flash(request, "Success", 'success')
    
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    redirect_url = f'/user_payments_account/{redirect_uuid}' if redirect_uuid else f'/payments_account'
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_302_FOUND)  

@payment_account_router.post('/update_payments_account')
async def user_payments_account(request: Request,
                                 user_uuid_hidden: UUID = Form(None)
                                ):
    form_list = (await request.form())._list
    user_uuid = form_list[0]
    if "user_uuid_hidden" in user_uuid:
        form_list.pop(0)
    else:
        pass
    for indx in range(0, len(form_list), 5):
        payment_account_uuid = form_list[indx][1]
        payment_account = await models.UserPaymentAccount.get(uuid=payment_account_uuid)
        user_uuid = form_list[indx+1][1]
        type_uuid = form_list[indx+2][1]
        data = form_list[indx+3][1]
        while "'" in data:
            data = data.replace("'", '"')
        # print(data)
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = payment_account.data
            flash(request, f"Invalid JSON - {data}", "danger")
        is_active = form_list[indx+4][1]
        if is_active == 'True':
            is_active = True
        else:
            is_active = False
        payment_account.update_from_dict({'user_id': user_uuid,
                                        'data': json_data,
                                        'type_id': type_uuid,
                                        'is_active': is_active
                                        })
        await payment_account.save()
        flash(request, "Success", "success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    
    redirect_url = f'/user_payments_account/{user_uuid_hidden}' if user_uuid_hidden else "/payments_account"
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_302_FOUND)  





# @payment_account_router.get("/sort/user_payments_account/{column}/{user_uuid}", response_class=RedirectResponse)
# @payment_account_router.get("/sort/payments_account/{column}", response_class=RedirectResponse)
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
    
#     redirect_url = f'/user_payments_account/{user_uuid}?' if user_uuid else "/payments_account?"
#     return redirect_url + urlencode(params)
