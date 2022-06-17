from uuid import UUID
from fastapi import APIRouter, Form, Request
from loader import flash
from models import models
from fastapi.responses import HTMLResponse, RedirectResponse
import starlette.status as status

history_balance_router = APIRouter()


@history_balance_router.post("/update_history_balance")
async def update_history_balance(request: Request,
                                 user_uuid_hidden: UUID = Form(None)
                                ):
    # history_balance = await models.UserBalanceChange.get(uuid=uuid)
    form_list = (await request.form())._list
    if user_uuid_hidden is not None:
        form_list.pop(0)
    for indx in range(0, len(form_list), 7):
        uuid_history_balance = form_list[indx][1]
        history_balance = await models.UserBalanceChange.get(uuid=uuid_history_balance)
        type = form_list[indx+1][1] 
        amount = form_list[indx+2][1] if form_list[indx+2][1] != "" else None
        hash = form_list[indx+3][1] if form_list[indx+3][1] != "" else None
        wallet = form_list[indx+4][1] if form_list[indx+4][1] != "" else None
        code = form_list[indx+5][1] if form_list[indx+5][1] != "" else None
        state = form_list[indx+6][1]
        history_balance.update_from_dict({"type": type, 
                                          "amount": amount, 
                                          "hash": hash, 
                                          "wallet": wallet, 
                                          "code": code, 
                                          "state": state})
        await history_balance.save()

    flash(request, "Success", category="success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
        f'/user/{user_uuid_hidden}' + params, 
        status_code=status.HTTP_302_FOUND)  