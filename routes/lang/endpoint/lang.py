from datetime import datetime
from typing import Union
from uuid import UUID
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel, validator
from models import models
from loader import templates, manager
from fastapi.responses import RedirectResponse
from starlette import status
from utils.models_utils import query_filters
from utils.order_by import order_by_utils
from utils.pagination import pagination
from tortoise.queryset import Q

lang_bot_text_router = APIRouter()

class LangSearch(BaseModel):
    rus__icontains: Union[str, None] = None
    rus__icontains: Union[str, None] = None
    updated_at__gte: Union[datetime, str] = None
    updated_at__lte: Union[datetime, str] = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None

    @validator("rus__icontains", 
               "rus__icontains", 
               "updated_at__gte",
               "updated_at__lte",
               "created_at__gte",
               "created_at__lte")
    def validate_str(cls, v):
        if v == "":
            return None
        else:
            return v


@lang_bot_text_router.get("/bot_text")
@lang_bot_text_router.get("/bot_button")
async def get_text_bot_lang(request: Request,
                            page: int = 1,
                            search: LangSearch = Depends(LangSearch),
                            order_by: str = None,
                            staff: models.Staff = Depends(manager)):
    query = Q(target_table__isnull=True)
    if request.url.path == "/bot_text":
        query &= Q(button=False)
    else:
        query &= Q(button=True)
    # print(search.rus__iconatins)
    query &= await query_filters(search)
    lang = models.Lang.filter(query)
    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await lang.count())
    order_by, order_by_args = order_by_utils(order_by)

    lang = lang.order_by(*order_by_args).offset(offset).limit(limit)

    context = {"request": request,
               "lang": await lang,
               'params': request.query_params._dict,
               'order_by': order_by,
               "page": page,
               "last_page": last_page,
               "previous_page": previous_page,
               "next_page": next_page,
               "url": request.url.path,
               "search": search}

    return templates.TemplateResponse('lang/lang.html', context)


@lang_bot_text_router.post("/update_bot_text")
async def update_bot_text(request: Request,
                          staff: models.Staff = Depends(manager)):
    form_list = (await request.form())._list
    for indx in range(0, len(form_list), 4):
        uuid = UUID(form_list[indx][1])
        rus = form_list[indx+1][1]
        eng = form_list[indx+2][1]
        description = form_list[indx+3][1]
        save = False

        lang = await models.Lang.get(uuid=uuid)
        if lang.rus != rus:
            lang.rus = rus
            save = True
        if lang.eng != eng:
            lang.eng = eng
            save = True
        if lang.description != description:
            lang.description = description
            save = True
        if save:
            await lang.save()
    return RedirectResponse(
        request.url_for("get_text_bot_lang"), 
        status_code=status.HTTP_302_FOUND)