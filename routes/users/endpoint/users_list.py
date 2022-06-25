from typing import List, Optional, Union
from datetime import datetime, timedelta
from urllib import parse
from uuid import UUID
from anyio import Any
from tortoise.queryset import Q
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from loader import templates, flash, manager
from urllib.parse import urlencode
import ast
import starlette.status as status
from utils.exceptions import NotAuthenticatedException

users_router = APIRouter()


@users_router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request,
                     user: models.Staff = Depends(manager),
                     username: str = None,
                     min_balance: float = None,
                     max_balance: float = None,
                     min_frozen_balance: float = None,
                     max_frozen_balance: float = None,
                     referal: Union[bool,str] = None,
                     lang: str = None,
                     min_created_at: datetime = None,
                     max_created_at: datetime = None,
                     order_by: str = None
                    ):
    if isinstance(referal, str):
        referal = None
    if lang == "":
        lang = None 

    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []
    query = Q()
    if username:
        query = query & Q(tg_username__icontains=username)
    if min_balance:
        query = query & Q(balance__gte=min_balance)
    if max_balance:
        query = query & Q(balance__lte=max_balance)
    if min_frozen_balance:
        query = query & Q(frozen_balance__gte=min_frozen_balance)
    if max_frozen_balance:
        query = query & Q(frozen_balance__lte=max_frozen_balance)
    if isinstance(referal, bool):
        query = query & Q(referal_user_id__isnull=referal)
    if lang:
        query = query & Q(lang=lang)
    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)

    if not min_balance:
        min_balance = 0
    if not max_balance:
        max_balance = await models.User.all().order_by("-balance").first().values("balance")
        max_balance = max_balance['balance']

    if not min_frozen_balance:
        min_frozen_balance = 0
    if not max_frozen_balance:
        max_frozen_balance = await models.User.all().order_by("-frozen_balance").first().values("frozen_balance")
        max_frozen_balance = max_frozen_balance['frozen_balance']
    
    if not min_created_at:
        min_created_at = datetime(year=2022, month=6, day=15, hour=0, minute=0, second=0)
        
    if not max_created_at:
        max_created_at = (datetime.utcnow() + timedelta(days=1))
        max_created_at = max_created_at.replace(microsecond=0)

    if len(order_by) == 0:
        users = await models.User.filter(query).order_by("-created_at")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        users = await models.User.filter(query).order_by(*order_by)
    context = {"request": request, 
               "users": users,
               "username": username,
               "min_balance": min_balance,
               "max_balance": max_balance,
               "min_frozen_balance": min_frozen_balance,
               "max_frozen_balance": max_frozen_balance,
               "referal": referal,
               "lang": lang,
               "min_created_at": min_created_at.isoformat(),
               "max_created_at": max_created_at.isoformat(),
               "order_by": order_by,
               "params": f"?{request.query_params}" if request.query_params != "" else "",
               }
    return templates.TemplateResponse("users/users_list.html", context)


# @users_router.get("/sort_user/{column}", response_class=RedirectResponse)
# async def sort_user(request: Request,
#                     column: str,
#                     user: models.Staff = Depends(manager)):
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
#     return "/users?" + urlencode(params)