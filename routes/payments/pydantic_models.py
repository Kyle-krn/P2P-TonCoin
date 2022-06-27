from datetime import datetime
from typing import Union
from uuid import UUID
from pydantic import BaseModel, validator


class PaymentsAccountSearch(BaseModel):
    uuid: Union[UUID, None] = None
    type_id: Union[UUID,str] = None
    currency_id: Union[UUID,str] = None
    is_active: Union[bool,str] = None
    updated_at__gte: Union[datetime, str] = None
    updated_at__lte: Union[datetime, str] = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None
    data__json: str = None
    
    @validator("type_id", 
               "currency_id", 
               "is_active",
               "updated_at__gte",
               "updated_at__lte",
               "created_at__gte",
               "created_at__lte")
    def validate_str(cls, v):
        if isinstance(v, str):
            return None
        else:
            return v


class PaymentsTypeSearch(BaseModel):
    currency_id: Union[UUID, str] = None
    name__icontains: Union[str, None] = None
    is_active: Union[bool,str] = None
    created_at__gte:Union[datetime, str] = None 
    created_at__lte:Union[datetime, str] = None 
    data__json: str = None

    @validator("currency_id", "is_active", "created_at__gte", "created_at__lte")
    def validate_str(cls, v):
        if isinstance(v, str):
            return None
        else:
            return v