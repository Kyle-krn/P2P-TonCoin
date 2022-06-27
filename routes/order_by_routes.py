import imp
from uuid import UUID
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from loader import manager
import ast
from urllib.parse import urlencode
from models import models


order_by_router = APIRouter()


@order_by_router.get("/sort/payments_account_type/{column}", response_class=RedirectResponse)

@order_by_router.get("/sort/user_payments_account/{column}/{user_uuid}", response_class=RedirectResponse)
@order_by_router.get("/sort/payments_account/{column}", response_class=RedirectResponse)

@order_by_router.get("/sort/users/{column}", response_class=RedirectResponse)

@order_by_router.get("/sort/currency/{column}", response_class=RedirectResponse)

@order_by_router.get("/sort/user_history_balance/{column}/{user_uuid}", response_class=RedirectResponse)
@order_by_router.get("/sort/history_balance/{column}", response_class=RedirectResponse)

@order_by_router.get("/sort/user_referal_children/{column}/{user_uuid}", response_class=RedirectResponse)
@order_by_router.get("/sort/referal_children/{column}", response_class=RedirectResponse)

@order_by_router.get("/sort/orders/{column}", response_class=RedirectResponse)
async def sort(request: Request,
                    column: str,
                    user_uuid: UUID = None,
                    staff: models.Staff = Depends(manager)):
    params = request.query_params._dict
    if "order_by" not in params:
        if column[0] != "~":
            params['order_by'] = [column]
    else:
        params['order_by'] = ast.literal_eval(params['order_by'])
        column_name = column[1:] 
        
        if column[0] == "~" and len([i for i in params["order_by"] if column_name == i[1:]]) > 0:
            params["order_by"] = [i for i in params["order_by"] if column_name != i[1:]]
        elif column[0] != "~":
            params["order_by"] = [i for i in params["order_by"] if column_name != i[1:]]
            params["order_by"].append(column)
    redirect_url = request.url.path.split('/')[2]
    redirect_url = f'/{redirect_url}/{user_uuid}?' if user_uuid else f"/{redirect_url}?"
    return redirect_url + urlencode(params)