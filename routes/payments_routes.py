import ast
from datetime import datetime
import json
from typing import Union
from urllib.parse import urlencode
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from loader import flash, manager, templates
from models import models
from tortoise.queryset import Q
import starlette.status as status


payment_account_router = APIRouter()

@payment_account_router.post('/update_payments_account')
async def user_payments_account(request: Request,
                                 user_uuid_hidden: UUID = Form(None)
                                ):
    form_list = (await request.form())._list
    if user_uuid_hidden is not None:
        form_list.pop(0)
    for indx in range(0, len(form_list), 4):
        payment_account_uuid = form_list[indx][1]
        payment_account = await models.UserPaymentAccount.get(uuid=payment_account_uuid)
        type_uuid = form_list[indx+1][1]
        data = form_list[indx+2][1]
        print(data)
        while "'" in data:
            data = data.replace("'", '"')
        # print(data)
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = payment_account.data
            flash(request, f"Invalid JSON - {data}", "danger")
        # data = [i for i in data.split("\n") if i != ""]
        # parse_data = {}
        # for i in data:
        #     if i != "\r":
        #         while "\r" in i: 
        #             i = i.replace("\r", "")
        #         parse_row = i.split('-')
        #         print(parse_row)
        #         try:
        #             key = parse_row[0]
        #             value = parse_row[1]
        #             parse_data[key] = value
        #         except IndexError:
        #             flash(request, f"Invalid string - {i}", "danger")
        is_active = form_list[indx+3][1]
        if is_active == 'True':
            is_active = True
        else:
            is_active = False
        payment_account.update_from_dict({
                                        'data': json_data,
                                        'type_id': type_uuid,
                                        'is_active': is_active
                                        })
        await payment_account.save()
        flash(request, "Success", "success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        f'/user_payments_account/{user_uuid_hidden}' + params, 
        status_code=status.HTTP_302_FOUND)  

@payment_account_router.get('/user_payments_account/{uuid}')
async def user_payment_account(request: Request,
                               uuid: UUID,
                               type_uuid: Union[UUID,str] = None,
                               currency_uuid: Union[UUID,str] = None,
                               payment_data: str = None,
                               is_active: Union[bool,str] = None,
                               min_updated_at: str = None,
                               max_updated_at: str = None,
                               min_created_at: str = None,
                               max_created_at: str = None,
                               page:int = 1):
    user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
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
    }
    payments_account = models.UserPaymentAccount.filter(user=user)
    
    query = Q()
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
        pass

    payments_account = payments_account.filter(query)

    limit = 5
    offset = (page - 1) * limit
    count_history_change = await payments_account.count()
    last_page = count_history_change/limit
    if count_history_change % limit == 0:
        last_page = int(last_page)
    elif count_history_change % limit != 0:
        last_page = int(last_page + 1)
    
    previous_page = page-1
    next_page = page+1
    if page == 1:
        previous_page = None
    if page == last_page:
        next_page = None
    if page > last_page:
        pass
    
    currency = await models.Currency.exclude(name="TON")
    payments_type = await models.UserPaymentAccountType.filter().prefetch_related("currency")
    payments_account = await payments_account.limit(limit).offset(offset).order_by('-created_at', 'uuid').prefetch_related("type__currency")

    context = {
        'request': request,
        'user': user,
        'params': request.query_params._dict,
        'payments_account': payments_account,
        'payments_type': payments_type,
        'currency': currency,
        'search': search,
        "page": page,
        "last_page": last_page,
        "previous_page": previous_page,
        "next_page": next_page,
    }

    
    return templates.TemplateResponse("user_payment_account.html", context)



