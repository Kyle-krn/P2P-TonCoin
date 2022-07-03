from datetime import datetime, timedelta
from urllib.parse import urlencode
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise import Tortoise
import os
from data import config
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
import typing
from fastapi_login import LoginManager
from models import models
from utils.exceptions import NotAuthenticatedException

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = Tortoise()

middleware = [Middleware(SessionMiddleware, secret_key="sdg905tigkog5ku54opg34m54.f34.f34l;tk34op2kfopw3igjp;")]
app = FastAPI(middleware=middleware)

SECRET = "secret-key"

manager = LoginManager(SECRET,
                       token_url="/auth/login",
                       use_cookie=True, 
                       default_expiry=timedelta(hours=12),
                       custom_exception=NotAuthenticatedException)
                       
manager.cookie_name = "access_token"

manager.useRequest(app)

templates = Jinja2Templates(directory="templates")

@manager.user_loader()
async def load_user(username:str):
    user = await models.Staff.get_or_none(login=username)
    return user


def get_urlencode(params: dict):
    str_params = urlencode(params)
    if len(str_params) > 0:
       str_params = "?" + str_params
    return str_params

def format_date(date: datetime):
    """Custom filter"""
    return date.strftime("%d %b %Y %X")


def format_float(item: float):
    if len(str(item).split('.')[1]) > 4:
        return "%.4f" % item 
    else:
        return item

def parse_payment_data(data: dict):
    """Custom filter"""
    text = ""
    for k,v in data.items():
        text += f"{k} - {v} <br>"
    return text



def flash(request: Request, message: typing.Any, category: str = "primary") -> None:
    if "_messages" not in request.session:
       request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})
       
def get_flashed_messages(request: Request):
   return request.session.pop("_messages") if "_messages" in request.session else []


templates.env.filters['get_urlencode'] = get_urlencode
templates.env.filters["format_date"] = format_date
templates.env.filters["parse_payment_data"] = parse_payment_data
templates.env.filters["format_float"] = format_float
templates.env.globals['get_flashed_messages'] = get_flashed_messages

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
