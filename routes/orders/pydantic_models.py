from datetime import datetime
from typing import Union
from uuid import UUID
from pydantic import BaseModel, validator


class SearchOrders(BaseModel):
    parent_id: Union[UUID, str] = None
    seller_id: Union[UUID, str] = None
    customer_id: Union[UUID, str] = None
    currency_id: Union[UUID, str] = None
    state: Union[str, None] = None
    amount__gte: Union[float, str] = None
    amount__lte: Union[float, str] = None
    origin_amount__gte: Union[float, str] = None
    origin_amount__lte: Union[float, str] = None
    margin__gte: Union[float, str] = None
    margin__lte: Union[float, str] = None
    commission__gte: Union[float, str] = None
    commission__lte: Union[float, str] = None
    final_price__gte: Union[float, str] = None
    final_price__lte: Union[float, str] = None
    min_buy_sum__gte: Union[float, str] = None
    min_buy_sum__lte: Union[float, str] = None
    updated_at__gte: Union[datetime, str] = None
    updated_at__lte: Union[datetime, str] = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None
    @validator("parent_id", 
               "seller_id", 
               "customer_id", 
               "currency_id", 
               "amount__gte", 
               "amount__lte", 
               "origin_amount__gte", 
               "origin_amount__lte", 
               "margin__gte", 
               "margin__lte", 
               "commission__gte", 
               "commission__lte", 
               "final_price__gte", 
               "final_price__lte", 
               "min_buy_sum__gte", 
               "min_buy_sum__lte",
               "updated_at__gte",
               "updated_at__lte",
               "created_at__gte",
               "created_at__lte")
    def validate_uuid(cls, v):
        if isinstance(v, str):
            return None
        else:
            return v
    
    @validator("state")
    def validate_state(cls, v):
        if v == "":
            return None
        else:
            return v