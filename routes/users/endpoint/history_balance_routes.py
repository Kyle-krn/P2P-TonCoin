from typing import Any, Union
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from models import models
from fastapi.responses import HTMLResponse, RedirectResponse
from loader import templates, flash, manager, bot
from aiogram.utils.exceptions import BotBlocked, ChatNotFound
from tortoise.queryset import Q
from utils import orm_utils
from utils.lang import lang_text
from starlette import status

history_balance_router = APIRouter()


@history_balance_router.get("/user_history_balance/{uuid}", response_class=HTMLResponse)
@history_balance_router.get("/history_balance", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID = None,
                      user_uuid: Union[UUID, Any] = None,
                      staff: models.Staff = Depends(manager),
                      type: str = None,
                      min_amount: Union[float, str] = None,
                      max_amount: Union[float, str] = None,
                      hash: str = None,
                      wallet: str = None,
                      state: str = None,
                      page: int = 1,
                      code: str = None,
                      min_created_at: str = None,
                      max_created_at: str = None,
                      order_by: str = None):
    if isinstance(user_uuid, UUID) is False:
        user_uuid = None
    if uuid:
        user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
        query = Q(user=user)
    else:
        user = None
        query = Q()
        
    history_balance_show = await models.UserBalanceChange.filter(query & Q(amount__isnull=False)).order_by('-amount').first().values("amount")
    search = {
        "type": None,
        "min_amount": 0,
        "max_amount_show": history_balance_show['amount'] if history_balance_show else None,
        "min_amount": None,
        "max_amount": None,
        "hash": None,
        "wallet": None,
        "code": None,
        "state": None,
        "min_created_at": None,
        "max_created_at": None,
        "user_uuid": None
    }

    if user_uuid:
        query = Q(user_id=user_uuid)
        search['user_uuid'] = user_uuid

    if type:
        query &= Q(type=type)
        search["type"] = type
    if min_amount:
        query &= Q(amount__gte=min_amount)
        search["min_amount"] = min_amount
    if max_amount:
        query &= Q(amount__lte=max_amount)
        search["max_amount"] = max_amount
    if hash:
        query &= Q(hash__icontains=hash)
        search["hash"] = hash
    if wallet:
        query &= Q(wallet__icontains=wallet)
        search["wallet"] = wallet
    if code:
        query &= Q(code__icontains=code)
        search["code"] = code
    if state:
        query &= Q(state=state)
        search["state"] = state

    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
        search["min_created_at"] = min_created_at
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)
        search["max_created_at"] = max_created_at
    
    history_balance = models.UserBalanceChange.filter(query)

    limit = 30
    offset, last_page, previous_page, next_page = orm_utils.pagination(limit=limit, page=page, count_model=await history_balance.count())
    order_by, order_by_args = orm_utils.order_by_utils(order_by)
    history_balance = history_balance.order_by(*order_by_args).offset(offset).limit(limit)
    
    prefetch_related = "user" if not user else None
    if prefetch_related:
        history_balance = await history_balance.prefetch_related(prefetch_related)
    else:
        history_balance = await history_balance
    params = request.query_params._dict
    context = {"request": request,
               "user": user,
               "params": params,
               "history_balance_search": search,
               "history_balance": history_balance,
               "page": page,
               "last_page": last_page,
               "previous_page": previous_page,
               "next_page": next_page,
               "order_by": order_by,
               "pagination_url": f"/user_history_balance/{user.uuid}" if user else "/history_balance"}
               
    template_name = "users/user_history_balance.html" if user else "history_balance.html"
    return templates.TemplateResponse(template_name, context)




@history_balance_router.get("/approve_withdraw/{history_uuid}", response_class=RedirectResponse)
@history_balance_router.get("/approve_withdraw/{user_uuid}/{history_uuid}", response_class=RedirectResponse)
@history_balance_router.get("/reject_withdraw/{history_uuid}", response_class=RedirectResponse)
@history_balance_router.get("/reject_withdraw/{user_uuid}/{history_uuid}", response_class=RedirectResponse)
async def update_withdraw(request: Request,
                          history_uuid: UUID,
                          user_uuid: UUID = None,
                          staff: models.Staff = Depends(manager),
                          ):
    history_balance = await models.UserBalanceChange.get_or_none(uuid=history_uuid)
    if history_balance is None:
        flash(request, "history balance not found", "danger")
    else:
        if history_balance.type == "withdraw" and history_balance.state == "created":
            user = await history_balance.user
            if request.url.path.split('/')[1] == "approve_withdraw":
                history_balance.state = "done"
                lang_uuid = "ad436ce0-a56a-4022-9222-9fc309b23c82"
            elif request.url.path.split('/')[1] == "reject_withdraw":
                history_balance.state = "cancelled"
                lang_uuid = "9055c931-a16b-4fb6-80c6-04d983cbae03"
                user.balance += history_balance.amount
                await user.save()

            await history_balance.save()
            text = await lang_text(lang_uuid=lang_uuid,
                           user=user,
                           format={
                                "amount":history_balance.amount,
                                "balance":user.balance    
                           })
            try:
                await bot.send_message(chat_id=user.telegram_id, text=text)
            except (BotBlocked, ChatNotFound):
                pass
            flash(request, "Success", "success")
        else:
            if history_balance.type != "withdraw":
                flash(request, "History balance not withdraw", "danger")
            if history_balance.state != "created":
                flash(request, "History balance not created", "danger")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    
    redirect_url = f"/user_history_balance/{user_uuid}" if user_uuid else "/history_balance"
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_302_FOUND)  

    
