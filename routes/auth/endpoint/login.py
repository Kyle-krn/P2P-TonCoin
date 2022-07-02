
from fastapi import Form, Request, APIRouter
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from loader import flash, load_user, manager, templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
from fastapi import Depends,status
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
import hashlib
from models import models

login_router = APIRouter()

@login_router.post("/auth/login")
async def login(request: Request, 
                data: OAuth2PasswordRequestForm = Depends()):
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
def logout(request: Request,
           staff = Depends(manager)):
   response = RedirectResponse(url="/auth/login")
   response.delete_cookie("access_token")
   return response


@login_router.get("/auth/login",response_class=HTMLResponse)
def loginwithCreds(request:Request):
    context = {"request": request}
    return templates.TemplateResponse("auth/login.html", context)

