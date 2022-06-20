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

user_router = APIRouter()


@user_router.get("/users", response_class=HTMLResponse)
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
    return templates.TemplateResponse("users_list.html", context)


@user_router.get("/sort_user/{column}", response_class=RedirectResponse)
async def sort_user(request: Request,
                    column: str,
                    user: models.Staff = Depends(manager)):
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
    return "/users?" + urlencode(params)


class NewChildrenExc(Exception):
    pass

@user_router.get("/user/{uuid}", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID,
                      user: models.Staff = Depends(manager)):
    user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
    context = {"request": request,
               "user": user,
               "params": request.query_params._dict}
    return templates.TemplateResponse("user_detail.html", context)


@user_router.post("/update_user/{user_uuid}")
async def update_user(request: Request,
                      user_uuid: UUID,
                      wallet: str = Form(None),
                      balance: float = Form(...),
                      frozen_balance: float = Form(...),
                      referal_parent: Union[UUID, Any] = Form(None),
                      user: models.Staff = Depends(manager),):
    user = await models.User.get(uuid=user_uuid)
    params = request.query_params
    if params != "":
        params = "?" + str(params)
   
    try:
        if referal_parent != user.referal_user_id:
            new_parent = None
            if referal_parent and isinstance(referal_parent, UUID):
                new_parent = await models.User.get_or_none(uuid=referal_parent)
                if new_parent is None or user == new_parent:
                    raise NewChildrenExc()
            old_referal = None
            if user.referal_user_id:
                old_referal = await models.UserReferalBonus.get(user_id=user.referal_user_id,
                                                                invited_user_id=user.uuid)
            if old_referal and new_parent is None:
                old_referal.state = "cancelled"
                user.referal_user = None
                await user.save()
                await old_referal.save()
            if old_referal is None and new_parent:
                new_referal = await models.UserReferalBonus.get_or_none(user_id=new_parent.uuid,
                                                                        invited_user_id=user.uuid)
                if not new_referal:
                    pass
                    new_referal = await models.UserReferalBonus.create(user_id=new_parent.uuid,
                                                           invited_user_id=user.uuid,
                                                           amount=1,
                                                           state="created")
                else:
                    new_referal.state = "created"
                    await new_referal.save()
                
                user.referal_user = new_parent
                await user.save()
            
            elif old_referal and new_parent:
                old_referal.state = "cancelled"
                await old_referal.save()
                new_referal = await models.UserReferalBonus.get_or_none(user_id=new_parent.uuid,
                                                                        invited_user_id=user.uuid)
                if not new_referal:
                    pass
                    new_referal = await models.UserReferalBonus.create(user_id=new_parent.uuid,
                                                           invited_user_id=user.uuid,
                                                           amount=1,
                                                           state="created")
                else:
                    new_referal.state = "created"
                    await new_referal.save()
                
                user.referal_user = new_parent
                await user.save()

            
    except NewChildrenExc:
        flash(request, "Invalid UUID")

    # if referal_parent != user.referal_user_id:
    #     if referal_parent is not None:
    #         if isinstance(referal_parent, UUID) is False or (await models.User.get_or_none(uuid=referal_parent)) is None or user.uuid == referal_parent:
    #             flash(request, "Error Parent UUID")
    #     else:
    #         if referal_parent is None and user.referal_user_id is not None:
    #             old_referal = await models.UserReferalBonus.get_or_none(user_id=user.referal_user_id,
    #                                                                     invited_user_id=user.uuid)  
    #             print(old_referal)
    #             if old_referal:
    #                 old_referal.state = "cancelled"
    #                 await old_referal.save()
    #             user.referal_user_id = None
    #         elif referal_parent is not None and user.referal_user_id is None:
    #             referal = await models.UserReferalBonus.get_or_none(user_id=referal_parent,
    #                                                 invited_user_id=user.uuid,
    #                                                 )
    #             if not referal:
    #                 await models.UserReferalBonus.create(user_id=referal_parent,
    #                                                 invited_user_id=user.uuid,
    #                                                 state="created",
    #                                                 amount=1)      
    #         else:
    #             old_referal = await models.UserReferalBonus.get_or_none(user_id=user.referal_user_id,
    #                                                                     invited_user_id=user.uuid)  
    #             if old_referal:
    #                 old_referal.state = "cancelled"
    #                 await old_referal.save()
                    
    #             referal = await models.UserReferalBonus.get_or_none(user_id=referal_parent,
    #                                                 invited_user_id=user.uuid,
    #                                                 )
    #             if not referal:
    #                 await models.UserReferalBonus.create(user_id=referal_parent,
    #                                                 invited_user_id=user.uuid,
    #                                                 state="created",
    #                                                 amount=1)

    await user.update_from_dict({"wallet": wallet, "balance": balance, "frozen_balance": frozen_balance})
    await user.save()
    flash(request, "Success", category="success")
    return RedirectResponse(
                            f'/user/{user_uuid}' + params, 
                            status_code=status.HTTP_302_FOUND
                            )        

    
    
    

