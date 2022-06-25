import ast
from typing import Any, Union
from urllib.parse import urlencode
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from loader import flash, manager, templates
from models import models
from tortoise.queryset import Q
import starlette.status as status

from utils.pagination import pagination

referal_router = APIRouter()

@referal_router.post("/create_referal")
async def create_referal_children(request: Request,
                                  redirect_uuid: UUID = Form(None),
                                  referal_parent_uuid: UUID = Form(),
                                  referal_children_uuid: Union[UUID, Any] = Form(),
                                  amount: float = Form()):
    if isinstance(referal_children_uuid, UUID) is False:
        flash(request, f"Invalid UUID: {referal_children_uuid}", "danger")
    elif referal_parent_uuid == referal_children_uuid:
        flash(request, f"Invalid UUID: {referal_children_uuid}", "danger")
    else: 
        referal = await models.UserReferalBonus.filter(user_id=referal_parent_uuid,
                                                            invited_user_id=referal_children_uuid)
        if len(referal) > 0:
            flash(request, f"Referal bonus already exists", "info")
        else:
            await models.UserReferalBonus.create(user_id=referal_parent_uuid,
                                                invited_user_id=referal_children_uuid,
                                                amount=amount,
                                                state="created")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    
    redirect_url = f'/user_referal_children/{redirect_uuid}' if redirect_uuid else "/referal_children"
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_302_FOUND)  

@referal_router.post("/update_referal_children")
async def update_referal_children(request: Request):
    form_list = (await request.form())._list
    user_uuid = form_list[0]
    if "user_uuid_hidden" in user_uuid:
        user_uuid = form_list.pop(0)
        user_uuid = user_uuid[1]
    else:
        user_uuid = None
    
    for indx in range(0, len(form_list), 3):
        uuid_referal = form_list[indx][1]
        state = form_list[indx+1][1] #if form_list[indx+2][1] != "" else None
        amount = form_list[indx+2][1]#if form_list[indx+3][1] != "" else None
        referal = await models.UserReferalBonus.get(uuid=uuid_referal)
        # old_uuid_children = referal.invited_user_id
        # new_uuid_children = form_list[indx+1][1]
        # if not new_uuid_children:
        #     flash(request, message="Empty children UUID", category="danger")
        #     continue
        # else:
        #     try:
        #         UUID(new_uuid_children)
        #         new_children = await models.User.get_or_none(uuid=new_uuid_children)
        #         if new_children is None:
        #             flash(request, message=f"{new_uuid_children} not exists")
        #             continue    
        #     except ValueError:
        #         flash(request, message=f"Invalid UUID - {new_uuid_children}")
        #         continue
        # if old_uuid_children != new_uuid_children:
        #     old_children: models.User = await referal.invited_user
        #     old_children.referal_user = None
        #     await old_children.save()
        #     new_children = await models.User.get(uuid=new_uuid_children)
        #     new_children.referal_user_id = new_uuid_children
        #     await new_children.save()
        #     referal.invited_user_id = new_uuid_children
        referal.amount = amount
        if referal.state != state:
            parent = await referal.user
            if (referal.state == 'created' or referal.state == 'cancelled') and state == "done":
                parent.balance += float(referal.amount)
                referal.state = state
                await parent.save()
            elif referal.state == 'done' and state == "cancelled":
                parent.balance -= float(referal.amount)
                referal.state = state
                await parent.save()
            elif (referal.state == 'done' or referal.state == 'cancelled') and state == "created":
                flash(request, "Если статус реферала равен 'cancelled' или 'done', то установить статус 'created' нельзя.")
            await referal.save()
    flash(request, "Success", category="success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    
    redirect_url = f'/user_referal_children/{user_uuid}' if user_uuid else "/referal_children"
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_302_FOUND)  


@referal_router.get("/user_referal_children/{uuid}", response_class=HTMLResponse)
@referal_router.get("/referal_children", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID = None,
                      staff: models.Staff = Depends(manager),
                      user_uuid: Union[UUID, str] = None,
                      invited_user_uuid: Union[UUID, str] = None,
                      state: str = None,
                      min_amount: Union[float, str] = None,
                      max_amount: Union[float, str] = None,
                      min_created_at: str = None,
                      max_created_at: str = None,
                      order_by: str = None,
                      page: int = 1
                      ):


    if user_uuid is not None and (isinstance(user_uuid, UUID) is False or (await models.User.get_or_none(uuid=user_uuid)) is None):
        user_uuid = None
        flash(request, "Error Parent UUID")

    if uuid:
        user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
        query = Q(user=user)
    else:
        user = None
        query = Q()


    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []

    search = {
        "invited_user_uuid": None,
        "state": None,
        "min_amount": None,
        "max_amount": None,
        "min_created_at": None,
        "max_created_at": None,
        "user_uuid": None
    }
    # query = Q(user=user)

    if user_uuid:
        query = Q(user_id=user_uuid)
        search['user_uuid'] = user_uuid

    if invited_user_uuid:
        if isinstance(invited_user_uuid, UUID) is False or (await models.User.get_or_none(uuid=invited_user_uuid)) is None:
            flash(request, "Error children UUID")
        else:
            query &= Q(invited_user_id=invited_user_uuid)
            search["invited_user_uuid"] = invited_user_uuid
    if state:
        query &= Q(state=state)
        search['state'] = state
    
    if min_amount:
        query = query & Q(amount__gte=min_amount)
        search['min_amount'] = min_amount
    if max_amount:
        query = query & Q(amount__lte=min_amount)
        search['max_amount'] = max_amount
    if min_created_at:
        query = query & Q(created_at__gte=min_created_at)
        search['min_created_at'] = min_created_at
    if max_created_at:
        query = query & Q(created_at__lte=max_created_at)
        search['max_created_at'] = max_created_at
    send_referal = models.UserReferalBonus.filter(query) #.

    if len(order_by) == 0:
        send_referal = send_referal.order_by("-created_at")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        send_referal = send_referal.order_by(*order_by)


    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await send_referal.count())
    send_referal = send_referal.offset(offset).limit(limit)

    send_referal = await send_referal.offset(offset).limit(limit).prefetch_related("invited_user", "user")
    context = {
        'request': request,
        'user': user,
        'params': request.query_params._dict,
        "send_referal": send_referal,
        "search": search,
        "order_by": order_by,
        "page": page,
        "last_page": last_page,
        "previous_page": previous_page,
        "next_page": next_page,
        "pagination_url": f"/user_referal_children/{user.uuid}" if user else "/referal_children",
    }
    template_name = "users/user_referal_children.html" if user else "referals.html"
    return templates.TemplateResponse(template_name, context)

