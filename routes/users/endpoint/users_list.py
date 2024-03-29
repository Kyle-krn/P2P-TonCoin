from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from models import models
from loader import templates, manager
from utils import orm_utils
from ..pydantic_models import UsersSearch


users_router = APIRouter()


@users_router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request,
                     staff: models.Staff = Depends(manager),
                     search: UsersSearch = Depends(UsersSearch),
                     order_by: str = None,
                     page: int = 1
                    ):
    print(search.created_at__gte, type(search.created_at__gte))
    query = await orm_utils.query_filters(search)
    users = models.User.filter(query)
    limit = 30
    offset, last_page, previous_page, next_page = orm_utils.pagination(limit=limit, page=page, count_model=await users.count())
    users = users.offset(offset).limit(limit)
    order_by, order_by_args = orm_utils.order_by_utils(order_by)
    users = await users.order_by(*order_by_args)
    context = {"request": request, 
               "users": users,
               "search": search,
               "order_by": order_by,
               "page": page,
               "last_page": last_page,
               "previous_page": previous_page,
               "next_page": next_page,
               "pagination_url": f"/users",
               "params": request.query_params._dict}
    return templates.TemplateResponse("users/users_list.html", context)