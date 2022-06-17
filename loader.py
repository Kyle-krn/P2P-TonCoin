from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise import Tortoise
import os
from data import config
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
import typing

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = Tortoise()

# app = FastAPI()
middleware = [
 Middleware(SessionMiddleware, secret_key="sdg905tigkog5ku54opg34m54.f34.f34l;tk34op2kfopw3igjp;")
]
app = FastAPI(middleware=middleware)


templates = Jinja2Templates(directory="templates")

def format_date(date: datetime):
    """Custom filter"""
    return date.strftime("%d %b %Y %X")


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

templates.env.filters["format_date"] = format_date
templates.env.filters["parse_payment_data"] = parse_payment_data
templates.env.globals['get_flashed_messages'] = get_flashed_messages

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
