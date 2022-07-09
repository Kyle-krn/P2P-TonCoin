from fastapi import APIRouter
from routes.users.endpoint import users_list, user, history_balance_routes, referal_routes

user_router = APIRouter()

user_router.include_router(users_list.users_router)
user_router.include_router(user.user_router)
user_router.include_router(history_balance_routes.history_balance_router)
user_router.include_router(referal_routes.referal_router)