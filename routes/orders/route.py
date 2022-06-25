from fastapi import APIRouter
from routes.orders.endpoint import list_orders
order_router = APIRouter()


order_router.include_router(list_orders.list_orders_router)