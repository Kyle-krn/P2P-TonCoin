from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, Request
from loader import templates, manager
from models import models
from utils.models_utils import query_filters
from utils.order_by import order_by_utils
from utils.pagination import pagination
from ..pydantic_models import CurrencySearch

get_currency_router = APIRouter()

@get_currency_router.get('/currency', response_class=HTMLResponse)
async def get_currency(request: Request,
                       staff: models.Staff = Depends(manager),
                       search: CurrencySearch = Depends(CurrencySearch),
                       order_by: str = None,
                       page: int = 1
                        ):
    ton_currency = await models.Currency.get(name="TON")
    query = await query_filters(search)
    currencies = models.Currency.filter(query).exclude(name="TON")
    limit = 5
    offset, last_page, previous_page, next_page = pagination(limit=limit, page=page, count_model=await currencies.count())
    order_by, order_by_args = order_by_utils(order_by)

    currencies = currencies.order_by(*order_by_args).offset(offset).limit(limit)
    
    currencies = await currencies
    for cur in currencies:
        lang_cur = await models.Lang.get_or_none(target_table="currency", target_id=cur.uuid)
        cur.rus = lang_cur.rus if lang_cur else None
        cur.eng = lang_cur.eng if lang_cur else None
    context = {
                "request": request,
                "ton_currency": ton_currency,
                "currencies": currencies,
                'search': search,
                'params': request.query_params._dict,
                'order_by': order_by,
                "page": page,
                "last_page": last_page,
                "previous_page": previous_page,
                "next_page": next_page,
                }
    return templates.TemplateResponse("currency.html", context)