
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from loader import flash, templates, manager
from models import models
from fastapi.responses import RedirectResponse
from starlette import status
from ..forms import UpdateOrderForm

detail_order_roter = APIRouter()


@detail_order_roter.get("/order/{uuid}")
async def order_detail(request: Request,
                       uuid: UUID = None,
                       staff: models.Staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid).prefetch_related("seller", "customer", "currency", "children_order")
    currencies = await models.Currency.exclude(name="TON")
    context = {"request": request,
               "order": order,
               "params": request.query_params._dict,
               "currencies": currencies}
    return templates.TemplateResponse("orders/detail_order.html", context)


@detail_order_roter.post("/update_order/{uuid}")
async def update_order(request: Request,
                       uuid: UUID,
                       staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid)
    form = UpdateOrderForm(request)
    await form.load_data()
    if await form.is_valid():
        save = False
        for k, v in form.__dict__.items():
            if k in ["request", "errors"]:
                continue
            if order.__dict__[k] != v:
                order.__dict__[k] = v
                save = True
        if save:
            await order.save()
    else:
        form.flash_error()
    return RedirectResponse(request.url_for('detail_order', uuid=order.uuid), status_code=status.HTTP_302_FOUND)





