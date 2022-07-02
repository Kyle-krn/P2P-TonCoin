from typing import Union
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from models import models
from loader import templates, manager
from utils.models_utils import query_filters
from utils.order_by import order_by_utils
from ..pydantic_models import UsersSearch


users_router = APIRouter()



@users_router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request,
                     staff: models.Staff = Depends(manager),
                     search: UsersSearch = Depends(UsersSearch),
                     order_by: str = None
                    ):    
    query = await query_filters(search)
    users = models.User.filter(query)
    order_by, order_by_args = order_by_utils(order_by)
    users = await users.order_by(*order_by_args)
    context = {"request": request, 
               "users": users,
               "search": search,
               "order_by": order_by,
               "params": f"?{request.query_params}" if request.query_params != "" else ""}
    return templates.TemplateResponse("users/users_list.html", context)