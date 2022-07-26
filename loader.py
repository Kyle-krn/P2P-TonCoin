from datetime import timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise import Tortoise
import os
from data import config
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi_login import LoginManager
from models import models
import utils.exceptions as custom_exc 
from utils.misc import logging

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
                       custom_exception=custom_exc.NotAuthenticatedException)
                       
manager.cookie_name = "access_token"

manager.useRequest(app)

templates = Jinja2Templates(directory="templates")

@manager.user_loader()
async def load_user(username:str):
    user = await models.Staff.get_or_none(login=username)
    return user


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
