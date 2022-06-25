from fastapi import APIRouter, Request, Depends
from loader import manager, templates
from fastapi.responses import RedirectResponse, HTMLResponse

from models import models

list_orders_router = APIRouter()


@list_orders_router.get('/orders')
async def list_orders(request: Request,
                      staff = Depends(manager)):
    orders = await models.Order.all()
    context = {
        'request': request,
        'orders': orders
    }
    return templates.TemplateResponse('/orders/list_orders.html', context)
