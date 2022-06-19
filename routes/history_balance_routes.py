import ast
from typing import Union
from urllib.parse import urlencode
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Request
from loader import flash
from models import models
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status
from loader import templates, flash, manager
from tortoise.queryset import Q

history_balance_router = APIRouter()


@history_balance_router.post("/update_history_balance")
async def update_history_balance(request: Request,
                                 user_uuid_hidden: UUID = Form(None)
                                ):
    form_list = (await request.form())._list
    if user_uuid_hidden is not None:
        form_list.pop(0)
    for indx in range(0, len(form_list), 7):
        uuid_history_balance = form_list[indx][1]
        history_balance = await models.UserBalanceChange.get(uuid=uuid_history_balance)
        type = form_list[indx+1][1] 
        amount = form_list[indx+2][1] if form_list[indx+2][1] != "" else None
        hash = form_list[indx+3][1] if form_list[indx+3][1] != "" else None
        wallet = form_list[indx+4][1] if form_list[indx+4][1] != "" else None
        code = form_list[indx+5][1] if form_list[indx+5][1] != "" else None
        state = form_list[indx+6][1]
        history_balance.update_from_dict({"type": type, 
                                          "amount": amount, 
                                          "hash": hash, 
                                          "wallet": wallet, 
                                          "code": code, 
                                          "state": state})
        await history_balance.save()
    flash(request, "Success", category="success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        f'/user_history_balance/{user_uuid_hidden}' + params, 
        status_code=status.HTTP_302_FOUND)  


@history_balance_router.get("/user_history_balance/{uuid}", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID,
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
    user = await models.User.get(uuid=uuid)
    history_balance = user.history_balance
    history_balance_show = await user.history_balance.filter(amount__isnull=False).order_by('-amount').first().values("amount")
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
    }

    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []

    query = Q()
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
        query &= Q(hash=state)
        search["state"] = state

    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
        search["min_created_at"] = min_created_at
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)
        search["max_created_at"] = max_created_at
    
    history_balance = history_balance.filter(query)
    limit = 5
    offset = (page - 1) * limit
    count_history_change = await history_balance.count()
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

    
    
    if len(order_by) == 0:
        history_balance = history_balance.order_by("-created_at")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        history_balance = history_balance.order_by(*order_by)
    
    history_balance = await history_balance.offset(offset).limit(limit)
    params = request.query_params._dict
    # print(params)
    # params = request.query_params
    # print(params)
    # if params == "":
    #     params = "?" + str(params)
    # print(params, len(params))
    context = {"request": request,
               "user": user,
               "params": params,
               "history_balance_search": search,
               "history_balance": history_balance,
               "history_balance_page": page,
               "history_balance_last_page": last_page,
               "history_balance_previous_page": previous_page,
               "history_balance_next_page": next_page,
               "order_by": order_by}

    return templates.TemplateResponse("user_history_balance.html", context)


@history_balance_router.get("/user_history_balance_sort/{user_uuid}/{column}", response_class=RedirectResponse)
async def sort_user(request: Request,
                    user_uuid: UUID,
                    column: str,
                    staff: models.Staff = Depends(manager)):
    params = request.query_params._dict
    if "order_by" not in params:
        if column[0] != "~":
            params['order_by'] = [column]
    else:
        params['order_by'] = ast.literal_eval(params['order_by'])
        column_name = column[1:] 
        
        if column[0] == "~" and len([i for i in params["order_by"] if column_name == i[1:]]) > 0:
            params["order_by"] = [i for i in params["order_by"] if column_name != i[1:]]
        elif column[0] != "~":
            params["order_by"] = [i for i in params["order_by"] if column_name != i[1:]]
            params["order_by"].append(column)
    return f"/user_history_balance/{user_uuid}?" + urlencode(params)
    # return "ok"