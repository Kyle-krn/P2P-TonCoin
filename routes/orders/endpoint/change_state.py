import imp
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from loader import templates, manager
from models import models
from fastapi.responses import RedirectResponse
from starlette import status
from ..forms import UpdateOrderStateForm
from utils.pagination import pagination

change_state_roter = APIRouter()

@change_state_roter.get("/change_state_order/{uuid}")
async def show_change_state_order(request: Request,
                             uuid: UUID,
                             page: int = 1,
                             staff: models.Staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid).prefetch_related("seller", "customer", "currency", "children_order")
    change_state_list = models.OrderStateChange.filter(order=order)
    limit = 30
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await change_state_list.count())
    change_state_list = await change_state_list.offset(offset).limit(limit).order_by("-created_at").prefetch_related("staff")
    context = {'request': request,
               'params': request.query_params._dict,
               "order": order,
               "proof": await order.proof_problem_order.all().first(),
               "order_change_state": change_state_list,
               "page": page,
               "last_page": last_page,
               "previous_page": previous_page,
               "next_page": next_page,
               "pagination_url": f"/change_state_order/{uuid}",}
    return templates.TemplateResponse("orders/order_change_state.html", context)



@change_state_roter.post("/update_state_order/{uuid}")
async def update_state_order(request: Request,
                             uuid: UUID,
                             staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid)
    form = UpdateOrderStateForm(request)
    await form.load_data()
    if form.is_valid():
        if order.state != form.state:
            await models.OrderStateChange.create(order=order, old_state=order.state, new_state=form.state, staff=staff, description=form.description)
            order.state = form.state
            await order.save()
    else:
        form.flash_error()
    return RedirectResponse(request.url_for("show_change_state_order", uuid=order.uuid), status_code=status.HTTP_302_FOUND)
