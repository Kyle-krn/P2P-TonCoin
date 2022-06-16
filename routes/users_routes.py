from typing import Optional, Union
from datetime import datetime, timedelta
from tortoise.queryset import Q
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from loader import templates

user_router = APIRouter()

@user_router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request,
                     username: str = None,
                     min_balance: float = None,
                     max_balance: float = None,
                     min_frozen_balance: float = None,
                     max_frozen_balance: float = None,
                     referal: Union[bool,str] = None,
                     lang: str = None,
                     min_created_at: datetime = None,
                     max_created_at: datetime = None,
                     ):
    

    if isinstance(referal, str):
        referal = None

    print(min_created_at)
    print(max_created_at)
    
    # if isinstance(min_created_at, str):
    #     min_created_at = None 
    # if isinstance(max_created_at, str):
    #     max_created_at = None 
    if lang == "":
        lang = None 

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

    
    users = await models.User.filter(query).order_by("-created_at")
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
               }
    return templates.TemplateResponse("users_list.html", context)
