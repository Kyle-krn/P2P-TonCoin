import ast
from typing import Union
from urllib.parse import urlencode
from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from loader import flash, manager, templates
from models import models
from tortoise.queryset import Q
import starlette.status as status

referal_router = APIRouter()

@referal_router.post("/update_referal_children")
async def update_history_balance(request: Request,
                                 user_uuid_hidden: UUID = Form(None)
                                ):
    form_list = (await request.form())._list
    # print(form_list)
    if user_uuid_hidden is not None:
        form_list.pop(0)
    for indx in range(0, len(form_list), 5):
        uuid_referal = form_list[indx][1]
        state = form_list[indx+2][1] #if form_list[indx+2][1] != "" else None
        amount = form_list[indx+3][1]#if form_list[indx+3][1] != "" else None
        delete_bool = form_list[indx+4][1]
        referal = await models.UserReferalBonus.get(uuid=uuid_referal)
        if delete_bool == 'True':
            children = await referal.invited_user
            children.referal_user = None
            await children.save()
            await referal.delete()
            continue
        
        old_uuid_children = referal.invited_user_id
        new_uuid_children = form_list[indx+1][1]
        if not new_uuid_children:
            flash(request, message="Empty children UUID", category="danger")
            continue
        else:
            try:
                UUID(new_uuid_children)
                new_children = await models.User.get_or_none(uuid=new_uuid_children)
                if new_children is None:
                    flash(request, message=f"{new_uuid_children} not exists")
                    continue    
            except ValueError:
                flash(request, message=f"Invalid UUID - {new_uuid_children}")
                continue
        if old_uuid_children != new_uuid_children:
            old_children: models.User = await referal.invited_user
            old_children.referal_user = None
            await old_children.save()
            new_children = await models.User.get(uuid=new_uuid_children)
            new_children.referal_user_id = new_uuid_children
            await new_children.save()
            referal.invited_user_id = new_uuid_children
        
        referal.state = state
        referal.amount = amount
        await referal.save()
    flash(request, "Success", category="success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        f'/user_referal_chidlren/{user_uuid_hidden}' + params, 
        status_code=status.HTTP_302_FOUND)  

@referal_router.get("/user_referal_chidlren/{uuid}", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID,
                      user: models.Staff = Depends(manager),
                      invited_user_uuid: Union[UUID, str] = None,
                      state: str = None,
                      min_amount: Union[float, str] = None,
                      max_amount: Union[float, str] = None,
                      min_created_at: str = None,
                      max_created_at: str = None,
                      order_by: str = None
                      ):
    user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
    
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
        "max_created_at": None
    }
    query = Q(user=user)
    if invited_user_uuid:
        if isinstance(invited_user_uuid, UUID) is False or (await models.User.get_or_none(uuid=invited_user_uuid)) is None:
            flash(request, "Error Parent UUID")
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

    send_referal = await send_referal.prefetch_related("invited_user")
    context = {
        'request': request,
        'user': user,
        'params': request.query_params._dict,
        "send_referal": send_referal,
        "search": search,
        "order_by": order_by
    }
    return templates.TemplateResponse("user_referal_children.html", context)


@referal_router.get("/user_referal_chidlren_sort/{user_uuid}/{column}", response_class=RedirectResponse)
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
    return f"/user_referal_chidlren/{user_uuid}?" + urlencode(params)