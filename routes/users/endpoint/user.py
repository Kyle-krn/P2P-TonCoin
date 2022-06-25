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
    return templates.TemplateResponse("users/user_detail.html", context)


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
                old_referal = await models.UserReferalBonus.get_or_none(user_id=user.referal_user_id,
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

    