
from typing import Union
from datetime import datetime
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
        if not v or v == 'None':
            return None
        else:
            return v