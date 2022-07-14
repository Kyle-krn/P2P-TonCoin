from ast import List
import json
from uuid import UUID
from fastapi import Request
import data
from tortoise.exceptions import DoesNotExist
from jinja_func import flash
from models import models


class CreatePaymentsTypeForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.name: str = None
        self.rus: str = None
        self.eng: str = None
        self.data: dict = None
        self.is_active: bool = None
        self.currency_id: UUID = None
    
    
    async def load_data(self):
        form = await self.request.form()
        self.name = form.get("name") if form.get("name") else None
        self.rus = form.get("rus") if form.get("rus") else None
        self.eng = form.get("eng") if form.get("eng") else None
        self.data = form.get("data") if form.get("data") else None
        self.is_active = True if form.get("is_active") else False
        self.currency_id = form.get("currency_id") if form.get("currency_id") else None
    
    async def is_valid(self):
        if not self.name:
            self.errors.append("Empty name")
        if not self.data:
            self.errors.append("Empty data")
        try:
            while "'" in self.data:
                self.data = self.data.replace("'", '"')
            self.data: dict = json.loads(self.data)
            for k,v in self.data.items():
                if isinstance(k, str):
                    k = k.strip()
                if isinstance(v, str):
                    v = v.strip()
                self.data[k] = v
        except (json.decoder.JSONDecodeError, TypeError):
            self.errors.append(f"Invalid JSON {self.data}")
        try:
            self.currency_id = UUID(self.currency_id)
            await models.Currency.get(uuid=self.currency_id)
        except (ValueError, TypeError, DoesNotExist):
            self.errors.append("Bad currency uuid")
        if (self.rus and not self.eng) or (not self.rus and self.eng):
            self.errors.append("Rus и Eng должны быть заполнены вместе, либо оба быть пустыми.")
        if not self.errors:
            return True
        return False

    def flash_error(self):
        for error in self.errors:
            flash(self.request, error, "danger")

        
class CreatePaymentsAccountForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: list = []
        self.user_uuid: UUID = None
        self.type_uuid: UUID = None
        self.data: dict = None
        self.is_active: bool = None    
    
    async def load_data(self):
        form = await self.request.form()
        self.user_uuid = form.get("user_uuid") if form.get("user_uuid") else None
        self.type_uuid = form.get("type_uuid") if form.get("type_uuid") else None
        self.data = form.get("data") if form.get("data") else None
        self.is_active = True if form.get("is_active") else False
    
    async def is_valid(self):

        try:
            self.user_uuid = UUID(self.user_uuid)
            await models.User.get(uuid=self.user_uuid)
        except (ValueError, TypeError, DoesNotExist) as exc:
            if isinstance(exc, DoesNotExist):
                self.errors.append("User not found")
            else:
                self.errors.append("Bad user UUID")
        
        try:
            self.type_uuid = UUID(self.type_uuid)
            await models.UserPaymentAccountType.get(uuid=self.type_uuid)
        except (ValueError, TypeError, DoesNotExist) as exc:
            if isinstance(exc, DoesNotExist):
                self.errors.append("Type not found")
            else:
                self.errors.append("Bad type UUID")
        
        try:
            while "'" in self.data:
                self.data = self.data.replace("'", '"')
            self.data: dict = json.loads(self.data)
            for k,v in self.data.items():
                if isinstance(k, str):
                    k = k.strip()
                if isinstance(v, str):
                    v = v.strip()
                self.data[k] = v
        except (json.decoder.JSONDecodeError, TypeError, ValueError):
            self.errors.append(f"Invalid JSON {self.data}")

        if not self.errors:
            return True
        return False

    def flash_error(self):
        for error in self.errors:
            flash(self.request, error, "danger")

        
