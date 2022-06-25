from fastapi import APIRouter
from routes.users.endpoint import users_list, user

user_router = APIRouter()

user_router.include_router(users_list.users_router)
user_router.include_router(user.user_router)