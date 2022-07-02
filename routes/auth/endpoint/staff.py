import hashlib
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse,HTMLResponse
from starlette import status
from loader import flash, templates, manager
from models import models
from utils.utils import str_bool
from tortoise.queryset import Q

register_router = APIRouter()

@register_router.get("/auth/register")
async def get_staff(request: Request,
                   staff_uuid: UUID = None,
                   login: str = None,
                   staff = Depends(manager)):
    query = Q()
    if staff_uuid:
        query &= Q(uuid=staff_uuid)
    if login:
        query &= Q(login=login)
    staffs = await models.Staff.filter(query)
    context = {"request": request,
               "staffs": staffs}
    return templates.TemplateResponse("auth/register.html", context)

@register_router.post("/auth/new_staff")
async def create_staff(request: Request,
                  username: str = Form(),
                  password: str = Form(),
                  superuser: bool = Form(False),
                  staff = Depends(manager)):
    hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
    await models.Staff.create(login=username, password=hashed_pass, superuser=superuser)
    flash(request, "Success", "success")
    return RedirectResponse(
                            f'/auth/register', 
                            status_code=status.HTTP_302_FOUND
                            )  

@register_router.post("/auth/update_staff")
async def update_staff(request: Request,
                       staff = Depends(manager)):
    form_list = (await request.form())._list
    print(form_list)
    for indx in range(0, len(form_list), 4):
        staff_uuid = form_list[indx][1]
        login = form_list[indx+1][1]
        superuser = str_bool(form_list[indx+2][1])
        delete = str_bool(form_list[indx+3][1])
        staff = await models.Staff.get(uuid=staff_uuid)
        if delete:
            await staff.delete()
        else:
            if staff.login != login:
                staff.login = login
            if staff.superuser != superuser:
                staff.superuser = superuser
            await staff.save()
    return RedirectResponse('/auth/register',
                            status_code=status.HTTP_302_FOUND)  