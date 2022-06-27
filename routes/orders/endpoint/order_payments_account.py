from uuid import UUID
from fastapi import APIRouter, Request, Form
from loader import templates
from models import models
from fastapi.responses import RedirectResponse
from starlette import status


order_payments_router = APIRouter()


@order_payments_router.get("/order_payments_account/{uuid}")
async def payments_order_account(request: Request,
                                 uuid: UUID):
    order = await models.Order.get(uuid=uuid).prefetch_related("seller", "customer", "currency", "children_order")
    filter_kwags = {"order": order}
    if order.parent:
        filter_kwags['order'] = await order.parent
    order_payments_account = await models.OrderUserPaymentAccount.filter(**filter_kwags).prefetch_related("account__type__currency")
    context = {
        "request": request,
        "order": order,
        "order_payments_account": order_payments_account,
    }
    return templates.TemplateResponse("orders/order_payments_account.html", context)
