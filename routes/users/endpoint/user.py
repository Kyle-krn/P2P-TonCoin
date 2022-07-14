from uuid import UUID
from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from loader import templates, manager
from jinja_func import flash
from ..forms import UserUpdateForm
import starlette.status as status


user_router = APIRouter()


@user_router.get("/user/{uuid}", response_class=HTMLResponse)
async def user_detail(request: Request, 
                      uuid: UUID,
                      staffs: models.Staff = Depends(manager)):
    user = await models.User.get(uuid=uuid).prefetch_related("referal_user")
    context = {"request": request,
               "user": user,
               "params": request.query_params._dict}
    return templates.TemplateResponse("users/user_detail.html", context)


@user_router.post("/update_user/{user_uuid}")
async def update_user(request: Request,
                      user_uuid: UUID,
                      staff: models.Staff = Depends(manager),):
    user = await models.User.get(uuid=user_uuid)
    form = UserUpdateForm(request)
    await form.load_data()
    if form.is_valid():
        save = False
        for k, v in form.__dict__.items():
            if k in ["request", "errors"]:
                continue
            if user.__dict__[k] != v:
                user.__dict__[k] = v
                save = True
        if save:
            flash(request, "Success", "success")
        if save:
            await user.save()
    else:
        form.flash_error()
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
                            f'/user/{user_uuid}' + params, 
                            status_code=status.HTTP_302_FOUND
                            )        

    