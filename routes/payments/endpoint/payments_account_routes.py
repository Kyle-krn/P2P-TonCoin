import json
from fastapi.responses import RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from tortoise.exceptions import DoesNotExist
from loader import templates, manager
from jinja_func import flash
from models import models
from tortoise.queryset import Q
import starlette.status as status
from ..forms import CreatePaymentsAccountForm
from ..pydantic_models import PaymentsAccountSearch
from utils import orm_utils, utils, custom_exc





payment_account_router = APIRouter()
    

@payment_account_router.get('/user_payments_account/{user_uuid}')
@payment_account_router.get('/payments_account')
async def user_payment_account(request: Request,
                               user_uuid: UUID = None,
                               search: PaymentsAccountSearch = Depends(PaymentsAccountSearch),
                               order_by: str = None,
                               page:int = 1,
                               staff: models.Staff = Depends(manager)):
    if user_uuid:
        user = await models.User.get(uuid=user_uuid).prefetch_related("referal_user")
        query = Q(user=user)
    else:
        user = None
        query = Q()

    query &= await orm_utils.query_filters(search)
    if search.data__json:
        uuid_list = await orm_utils.rowsql_get_distinct_list_value(search.data__json, table="user_payment_account")
        uuid_list = [i['uuid'] for i in uuid_list]
        query &= Q(uuid__in=uuid_list)

    payments_account = models.UserPaymentAccount.filter(query)
  

    payments_account = payments_account.filter(query)

    limit = 30
    offset, last_page, previous_page, next_page = orm_utils.pagination(limit=limit, page=page, count_model=await payments_account.count())
    payments_account = payments_account.offset(offset).limit(limit)
    
    currency = await models.Currency.exclude(name="TON")
    payments_type = await models.UserPaymentAccountType.filter().prefetch_related("currency")

    order_by, order_by_args = orm_utils.order_by_utils(order_by)
    payments_account = payments_account.order_by(*order_by_args)

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
                                  staff: models.Staff = Depends(manager)):
    form = CreatePaymentsAccountForm(request)
    await form.load_data()
    if await form.is_valid():
        await models.UserPaymentAccount.create(user_id=form.user_uuid,
                                                   type_id=form.type_uuid,
                                                   data=form.data,
                                                   is_active=form.is_active)
        flash(request, "Success created", "success")
    else:
        form.flash_error()
   
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    redirect_url = f'/user_payments_account/{redirect_uuid}' if redirect_uuid else f'/payments_account'
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_303_SEE_OTHER)  


@payment_account_router.post('/update_payments_account')
async def user_payments_account(request: Request,
                                user_uuid_hidden: UUID = Form(None),
                                staff: models.Staff = Depends(manager)
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
        try:
            json_data = json.loads(data)
        except json.decoder.JSONDecodeError:
            json_data = payment_account.data
            flash(request, f"Invalid JSON - {data}", "danger")
        is_active = utils.str_bool(form_list[indx+4][1])
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
        status_code=status.HTTP_303_SEE_OTHER)  



@payment_account_router.get('/delete_payments_account/{payments_account_uuid}')
async def delete_payments_account(request: Request,
                                 payments_account_uuid: UUID,
                                 staff: models.Staff = Depends(manager)):
    try:
        payments_account = await models.UserPaymentAccount.get(uuid=payments_account_uuid)
        order_user_payment_account = await payments_account.order_user_payment_account.all()
        if len(order_user_payment_account) > 0:
            raise custom_exc.OrderPaymentsAccountNotEmpty
       
        await payments_account.delete()

    except (custom_exc.OrderPaymentsAccountNotEmpty, DoesNotExist) as exc:
        if isinstance(exc, custom_exc.OrderPaymentsAccountNotEmpty):
            flash(request, "Платежный аккаунт имеет заказы", "danger")
        if isinstance(exc, DoesNotExist):
            flash(request, "Аккаунт не найден", "danger")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        request.url_for('user_payment_account') + params, 
        status_code=status.HTTP_303_SEE_OTHER) 
