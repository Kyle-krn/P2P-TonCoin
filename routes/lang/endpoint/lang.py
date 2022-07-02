from uuid import UUID
from fastapi import APIRouter, Request
from models import models
from loader import templates
from fastapi.responses import RedirectResponse
from starlette import status
from utils.order_by import order_by_utils
from utils.pagination import pagination


lang_bot_text_router = APIRouter()


@lang_bot_text_router.get("/bot_text")
async def get_text_bot_lang(request: Request,
                            page: int = 1,
                            order_by: str = None):
    lang = models.Lang.filter(target_table__isnull=True, button=False)
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
               "next_page": next_page}

    return templates.TemplateResponse('lang/lang.html', context)


@lang_bot_text_router.post("/update_bot_text")
async def update_bot_text(request: Request):
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