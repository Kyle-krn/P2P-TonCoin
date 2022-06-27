from fastapi import APIRouter
from routes.orders.endpoint import list_orders, detail_order, change_state, change_amount, order_payments_account
order_router = APIRouter()


order_router.include_router(list_orders.list_orders_router)
order_router.include_router(detail_order.detail_order_roter)
order_router.include_router(change_state.change_state_roter)
order_router.include_router(change_amount.change_amount_roter)
order_router.include_router(order_payments_account.order_payments_router)