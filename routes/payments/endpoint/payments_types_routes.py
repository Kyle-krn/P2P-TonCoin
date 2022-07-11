import json
from typing import Union
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from loader import flash, templates, manager
from models import models
from tortoise.queryset import Q
from tortoise.exceptions import DoesNotExist
import starlette.status as status
from utils import orm_utils
# from utils.models_utils import query_filters
# from utils.order_by import order_by_utils
# from utils.search_db_json import rowsql_get_distinct_list_value
from utils.utils import str_bool
from tortoise.exceptions import DoesNotExist
from ..forms import CreatePaymentsTypeForm
from ..pydantic_models import PaymentsTypeSearch
from utils import custom_exc, orm_utils 

payments_type_router = APIRouter()


@payments_type_router.get("/payments_account_type", response_class=HTMLResponse)
async def payments_account_type(request: Request,
                                search: PaymentsTypeSearch = Depends(PaymentsTypeSearch),
                                order_by: str = None,
                                staff: models.Staff = Depends(manager)):
    currencies = await models.Currency.exclude(name="TON")
    query = await orm_utils.query_filters(search)
    if search.data__json:
        uuid_list = await orm_utils.rowsql_get_distinct_list_value(search.data__json, table="user_payment_account_type")
        uuid_list = [i['uuid'] for i in uuid_list]
        query &= Q(uuid__in=uuid_list)

    payment_types = models.UserPaymentAccountType.filter(query)
    order_by, order_by_args = orm_utils.order_by_utils(order_by)
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



@payments_type_router.post('/create_payments_account_type')
async def create_payments_account_type(request: Request,
                                  staff: models.Staff = Depends(manager)):
    form = CreatePaymentsTypeForm(request)
    await form.load_data()
    if await form.is_valid():
        type = await models.UserPaymentAccountType.create(name=form.name, 
                                                   data=form.data, 
                                                   is_active=form.is_active,
                                                   currency_id=form.currency_id)
        if form.rus and form.eng:
            await models.Lang.create(target_table="user_payment_account_type", target_uuid=type.uuid, rus=form.rus, eng=form.eng)
        flash(request, "Success create", "success")
    else:
        form.flash_error()
    params = request.query_params
    
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        request.url_for('payments_account_type') + params, 
        status_code=status.HTTP_302_FOUND) 




@payments_type_router.get('/delete_payments_account_type/{type_uuid}')
async def delete_payments_account_type(request: Request,
                                       type_uuid: UUID,
                                       staff: models.Staff = Depends(manager)):
    try:
        type = await models.UserPaymentAccountType.get(uuid=type_uuid)
        payments_account = await type.payments_account.all()
        if len(payments_account) > 0:
            raise custom_exc.PaymentsAccountNotEmpty
        orders = await type.customer_pay_type.all()
        if len(orders) > 0:
            raise custom_exc.OrderNotEmpty
        await type.delete()
    except (custom_exc.PaymentsAccountNotEmpty, custom_exc.OrderNotEmpty, DoesNotExist) as exc:
        if isinstance(exc, custom_exc.PaymentsAccountNotEmpty):
            flash(request, "Тип имеет платежные аккаунты", "danger")
        if isinstance(exc, custom_exc.OrderNotEmpty):
            flash(request, "Тип имеет заказы", "danger")
        if isinstance(exc, DoesNotExist):
            flash(request, "Тип не найден", "danger")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        request.url_for('payments_account_type') + params, 
        status_code=status.HTTP_302_FOUND) 
