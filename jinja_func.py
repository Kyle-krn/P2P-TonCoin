
import datetime
import typing
from urllib.parse import urlencode
from loader import templates
from fastapi import Request


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