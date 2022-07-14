from typing import Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, validator


class UsersSearch(BaseModel):
    tg_username__icontains: Union[str, None] = None
    balance__gte: Union[float, str] = None
    balance__lte: Union[float, str] = None
    frozen_balance__gte: Union[float, str] = None
    frozen_balance__lte: Union[float, str] = None
    referal_user_id__isnull: Union[bool, str] = None
    lang: Union[str, None] = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None
    
    @validator("tg_username__icontains", 
               "balance__gte", 
               "balance__lte",
               "frozen_balance__gte",
               "frozen_balance__lte",
               "referal_user_id__isnull",
               "lang",
               "created_at__gte",
               "created_at__lte")
    def validate_str(cls, v):
        if v == "" or v == 'None':
            return None
        else:
            return v


class ReferalSearch(BaseModel):
    user_id: Union[UUID,str] = None
    invited_user_id: Union[UUID,str] = None
    state: str = None
    amount__gte: Union[float, str] = None
    amount__lte: Union[float, str] = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None

    @validator("user_id",
               "invited_user_id",
               "amount__gte",
               "amount__lte",
               "created_at__gte",
               "created_at__lte"
              )
    def validate(cls, v):
        if isinstance(v, str):
            return None
        return v
    
    @validator("state")
    def validate_state(cls, v):
        if v not in ("created" ,"done" ,"cancelled"):
            return None
        return v



class HistoryBalanceSearch(BaseModel):
    user_id: Union[UUID,str] = None
    type: str = None
    amount__gte: Union[float, str] = None
    amount__lte: Union[float, str] = None
    hash: str = None
    wallet: str = None
    state: str = None
    code: str = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None


    @validator("user_id",
               "amount__gte",
               "amount__lte",
               "created_at__gte",
               "created_at__lte"
               )
    def validate(cls, v):
        if isinstance(v, str):
            return None
        return v
    

    @validator("type",
               "hash",
               "wallet",
               "state",
               "code")
    def validate_str(cls, v):
        if v == "":
            return None
        return v