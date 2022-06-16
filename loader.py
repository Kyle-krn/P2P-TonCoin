from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tortoise import Tortoise
import os
from data import config
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = Tortoise()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def format_date(date: datetime):
    """Custom filter"""
    return date.strftime("%d %b %Y %X")


templates.env.filters["format_date"] = format_date

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
