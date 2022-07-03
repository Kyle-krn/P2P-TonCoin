import imp
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from loader import templates, manager
from models import models
from fastapi.responses import RedirectResponse
from starlette import status
from ..forms import UpdateOrderAmountForm
from utils.pagination import pagination

change_amount_roter = APIRouter()


@change_amount_roter.get("/change_amount_order/{uuid}")
async def show_change_amount_order(request: Request,
                             uuid: UUID,
                             page: int = 1,
                             staff: models.Staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid).prefetch_related("seller", "customer", "currency", "children_order")
    change_amount_list = models.OrderAmountChange.filter(order=order)
    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await change_amount_list.count())
    change_amount_list = await change_amount_list.offset(offset).limit(limit).order_by("-created_at").prefetch_related("staff", "target_order")
    context = {'request': request,
               'params': request.query_params._dict,
               "order": order,
               "order_change_amount": change_amount_list,
               "page": page,
               "last_page": last_page,
               "previous_page": previous_page,
               "next_page": next_page,
               "pagination_url": f"/change_state_order/{uuid}",}
    return templates.TemplateResponse("orders/order_change_amount.html", context)



@change_amount_roter.post("/update_amount_order/{uuid}")
async def update_amount_order(request: Request,
                              uuid: UUID,
                              staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid)
    form = UpdateOrderAmountForm(request)
    await form.load_data()
    if form.is_valid():
        if order.amount != form.amount:
            await models.OrderAmountChange.create(order=order, old_amount=order.amount, new_amount=form.amount, staff=staff, description=form.description)
            order.amount = form.amount
            await order.save()
    else:
        form.flash_error()
    return RedirectResponse(request.url_for("show_change_amount_order", uuid=order.uuid), status_code=status.HTTP_302_FOUND)
