from fastapi import Form, Request, APIRouter
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from loader import flash, manager, templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
from fastapi import Depends,status
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
import hashlib
from models import models

login_router = APIRouter()



@manager.user_loader
async def load_user(username:str):
    user = await models.Staff.get_or_none(login=username)
    return user


async def load_superuser(user=Depends(manager)):
    return None


@login_router.get("/auth/register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@login_router.post("/auth/new_staff")
async def post_register(request: Request,
                  username: str = Form(),
                  password: str = Form(),
                  superuser: bool = Form(False)):
    hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
    await models.Staff.create(login=username, password=hashed_pass, superuser=superuser)
    flash(request, "Success", "success")
    return RedirectResponse(
                            f'/auth/register', 
                            status_code=status.HTTP_302_FOUND
                            )  

@login_router.post("/auth/login")
async def login(request: Request, data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password
    hashed_pass = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user = await load_user(username)
    if not user:
        flash(request, "Invalid Creedlines", category="dunger")
        return RedirectResponse(
                            f'/auth/login', 
                            status_code=status.HTTP_302_FOUND
                            )  
    elif hashed_pass != user.password:
        flash(request, "Invalid Creedlines", category="dunger")
        return RedirectResponse(
                            f'/auth/login', 
                            status_code=status.HTTP_302_FOUND
                            )
    access_token = manager.create_access_token(
        data={"sub":username}
    )
    resp = RedirectResponse(url="/users",status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp


@login_router.get("/auth/logout", response_class=HTMLResponse)
def logout(request: Request):
   response = RedirectResponse(url="/auth/login")
   response.delete_cookie("access_token")
   return response


@login_router.get("/auth/login",response_class=HTMLResponse)
def loginwithCreds(request:Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context)

