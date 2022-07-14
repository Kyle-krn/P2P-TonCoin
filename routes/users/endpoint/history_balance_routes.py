from uuid import UUID
from fastapi import APIRouter, Depends, Request
from models import models
from fastapi.responses import HTMLResponse, RedirectResponse
from loader import templates, manager, bot
from jinja_func import flash
from aiogram.utils.exceptions import BotBlocked, ChatNotFound
from tortoise.queryset import Q
from utils import orm_utils
from utils.lang import lang_text
from starlette import status
from ..pydantic_models import HistoryBalanceSearch

history_balance_router = APIRouter()


@history_balance_router.get("/user_history_balance/{uuid}", response_class=HTMLResponse)
@history_balance_router.get("/history_balance", response_class=HTMLResponse)
async def get_history_balance(request: Request, 
                      uuid: UUID = None,
                      search: HistoryBalanceSearch = Depends(HistoryBalanceSearch),
                      staff: models.Staff = Depends(manager),
                      order_by: str = None,
                      page: int = 1):

    if uuid:
        user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
        query = Q(user=user)
    else:
        user = None
        query = Q()
    
    query &= await orm_utils.query_filters(search)

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

    
