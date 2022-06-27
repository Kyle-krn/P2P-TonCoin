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
from utils.order_by import order_by_utils

from utils.pagination import pagination

history_balance_router = APIRouter()


# @history_balance_router.post("/update_history_balance")
# async def update_history_balance(request: Request,
#                                  user_uuid_hidden: UUID = Form(None)
#                                 ):
#     form_list = (await request.form())._list
#     if user_uuid_hidden is not None:
#         form_list.pop(0)
#     for indx in range(0, len(form_list), 7):
#         uuid_history_balance = form_list[indx][1]
#         history_balance = await models.UserBalanceChange.get(uuid=uuid_history_balance)
#         type = form_list[indx+1][1] 
#         amount = form_list[indx+2][1] if form_list[indx+2][1] != "" else None
#         hash = form_list[indx+3][1] if form_list[indx+3][1] != "" else None
#         wallet = form_list[indx+4][1] if form_list[indx+4][1] != "" else None
#         code = form_list[indx+5][1] if form_list[indx+5][1] != "" else None
#         state = form_list[indx+6][1]
#         history_balance.update_from_dict({"type": type, 
#                                           "amount": amount, 
#                                           "hash": hash, 
#                                           "wallet": wallet, 
#                                           "code": code, 
#                                           "state": state})
#         await history_balance.save()
#     flash(request, "Success", category="success")
#     params = request.query_params
#     if params != "":
#         params = "?" + str(params)
#     return RedirectResponse(
#         f'/user_history_balance/{user_uuid_hidden}' + params, 
#         status_code=status.HTTP_302_FOUND)  


@history_balance_router.get("/user_history_balance/{uuid}", response_class=HTMLResponse)
@history_balance_router.get("/history_balance", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID = None,
                      user_uuid: Union[UUID, Any] = None,
                      user: models.Staff = Depends(manager),
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

    # if order_by:
    #     order_by = ast.literal_eval(order_by)
    # else:
    #     order_by = []

    if user_uuid:
        query = Q(user_id=user_uuid)
        search['user_uuid'] = user_uuid
    # else:
    #     query = Q()
    # filter_dict = [
    #                 {"type": type, }
    # ]
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

    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await history_balance.count())
    order_by, order_by_args = order_by_utils(order_by)
    history_balance = history_balance.order_by(*order_by_args).offset(offset).limit(limit)
    
    
    # if len(order_by) == 0:
    #     history_balance = history_balance.order_by("-created_at")
    # else:
    #     for item in order_by:
    #         if item[0] == "+":
    #             indx = order_by.index(item)
    #             order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
    #     history_balance = history_balance.order_by(*order_by)
    
   
    
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


    


