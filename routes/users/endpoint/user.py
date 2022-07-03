from uuid import UUID
from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from loader import templates, flash, manager
from ..forms import UserUpdateForm
import starlette.status as status


user_router = APIRouter()


class NewChildrenExc(Exception):
    pass

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
    # try:
    #     if referal_parent != user.referal_user_id:
    #         new_parent = None
    #         if referal_parent and isinstance(referal_parent, UUID):
    #             new_parent = await models.User.get_or_none(uuid=referal_parent)
    #             if new_parent is None or user == new_parent:
    #                 raise NewChildrenExc()
    #         old_referal = None
    #         if user.referal_user_id:
    #             old_referal = await models.UserReferalBonus.get_or_none(user_id=user.referal_user_id,
    #                                                             invited_user_id=user.uuid)
    #         if old_referal and new_parent is None:
    #             old_referal.state = "cancelled"
    #             user.referal_user = None
    #             await user.save()
    #             await old_referal.save()
    #         if old_referal is None and new_parent:
    #             new_referal = await models.UserReferalBonus.get_or_none(user_id=new_parent.uuid,
    #                                                                     invited_user_id=user.uuid)
    #             if not new_referal:
    #                 pass
    #                 new_referal = await models.UserReferalBonus.create(user_id=new_parent.uuid,
    #                                                        invited_user_id=user.uuid,
    #                                                        amount=1,
    #                                                        state="created")
    #             else:
    #                 new_referal.state = "created"
    #                 await new_referal.save()
                
    #             user.referal_user = new_parent
    #             await user.save()
            
    #         elif old_referal and new_parent:
    #             old_referal.state = "cancelled"
    #             await old_referal.save()
    #             new_referal = await models.UserReferalBonus.get_or_none(user_id=new_parent.uuid,
    #                                                                     invited_user_id=user.uuid)
    #             if not new_referal:
    #                 pass
    #                 new_referal = await models.UserReferalBonus.create(user_id=new_parent.uuid,
    #                                                        invited_user_id=user.uuid,
    #                                                        amount=1,
    #                                                        state="created")
    #             else:
    #                 new_referal.state = "created"
    #                 await new_referal.save()
                
    #             user.referal_user = new_parent
    #             await user.save()

            
    # except NewChildrenExc:
    #     flash(request, "Invalid UUID")

  
    # await user.update_from_dict({"wallet": wallet, "balance": balance, "frozen_balance": frozen_balance})
    # await user.save()
    # flash(request, "Success", category="success")
    params = request.query_params
    if params != "":
        params = "?" + str(params)
    return RedirectResponse(
                            f'/user/{user_uuid}' + params, 
                            status_code=status.HTTP_302_FOUND
                            )        

    