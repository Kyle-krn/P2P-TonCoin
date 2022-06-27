from fastapi import APIRouter, Request, Depends
from loader import manager, templates
from models import models
from utils.models_utils import query_filters
from utils.order_by import order_by_utils
from utils.pagination import pagination
from ..pydantic_models import SearchOrders
from tortoise.queryset import Q

list_orders_router = APIRouter()



@list_orders_router.get('/orders')
async def list_orders(request: Request,
                      search_orders: SearchOrders = Depends(SearchOrders),
                      staff = Depends(manager),
                      order_by: str = None,
                      page: int = 1):
    query = await query_filters(search_orders)
    orders = models.Order.filter(query)
    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await orders.count())
    orders = orders.offset(offset).limit(limit)
    order_by, order_by_args = order_by_utils(order_by)
    orders = orders.order_by(*order_by_args)
    orders = await orders.prefetch_related("seller", "customer", "parent", "currency")
    currencies = await models.Currency.exclude(name="TON")
    context = {
        'request': request,
        "params": request.query_params._dict,
        'orders': orders,
        "currencies": currencies,
        "page": page,
        "last_page": last_page,
        "previous_page": previous_page,
        "next_page": next_page,
        "pagination_url": f"/orders",
        "order_by": order_by,
        "search": search_orders
    }

    return templates.TemplateResponse('/orders/list_orders.html', context)
