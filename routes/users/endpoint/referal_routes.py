from fastapi.responses import HTMLResponse, RedirectResponse
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from loader import manager, templates
from jinja_func import flash
from models import models
from tortoise.queryset import Q
import starlette.status as status
from utils import orm_utils
from loader import bot
from utils.lang import lang_text
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from ..pydantic_models import ReferalSearch
from ..forms import CreateReferalForm

referal_router = APIRouter()


@referal_router.post("/create_referal")
async def create_referal_children(request: Request,
                                  staff: models.Staff = Depends(manager)):
    form = CreateReferalForm(request)
    await form.load_data()
    if await form.is_valid():
        await models.UserReferalBonus.create(user_id=form.user_id,
                                             invited_user_id=form.invited_user_id,
                                             amount=form.amount,
                                             state="created")
        flash(request, "Success", "success")
    else:
        form.flash_error()
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    redirect_url = f'/user_referal_children/{form.redirect_uuid}' if form.redirect_uuid else "/referal_children"
    return RedirectResponse(
        redirect_url + params, 
        status_code=status.HTTP_302_FOUND)  



@referal_router.post("/update_referal_children")
async def update_referal_children(request: Request,
                                  staff: models.Staff = Depends(manager)):
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
        referal.amount = amount
        if referal.state != state:
            parent = await referal.user
            if (referal.state == 'created' or referal.state == 'cancelled') and state == "done":
                parent.balance += float(referal.amount)
                try:
                    text = await lang_text(lang_uuid="743374c9-84e8-4336-a8e9-49b1e70b7b68",
                                           user=parent,
                                           format={"amount": float(referal.amount)})
                    await bot.send_message(chat_id=parent.telegram_id, 
                                           text=text)
                except (ChatNotFound, BotBlocked):
                    pass
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



@referal_router.get("/user_referal_children/{user_uuid}", response_class=HTMLResponse)
@referal_router.get("/referal_children", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      user_uuid: UUID = None,
                      staff: models.Staff = Depends(manager),
                      search: ReferalSearch = Depends(ReferalSearch),
                      order_by: str = None,
                      page: int = 1
                      ):

    if user_uuid:
        user = await models.User.get(uuid=user_uuid).prefetch_related("referal_user")
        query = Q(user=user)
    else:
        user = None
        query = Q()
        
    query &= await orm_utils.query_filters(search)
    send_referal = models.UserReferalBonus.filter(query) 

    limit = 30
    offset, last_page, previous_page, next_page = orm_utils.pagination(limit=limit, page=page, count_model=await send_referal.count())
    order_by, order_by_args = orm_utils.order_by_utils(order_by)
    send_referal = send_referal.order_by(*order_by_args).offset(offset).limit(limit)

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

