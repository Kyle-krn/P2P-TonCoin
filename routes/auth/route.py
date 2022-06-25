from fastapi import APIRouter
from routes.auth.endpoint import login, staff

auth_router = APIRouter()


auth_router.include_router(staff.register_router)
auth_router.include_router(login.login_router)