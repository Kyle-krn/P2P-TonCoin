from datetime import datetime
from typing import Union
from pydantic import BaseModel, validator


class CurrencySearch(BaseModel):
    name__icontains: Union[str, None] = None
    exchange_rate__gte: Union[float, str] = None
    exchange_rate__lte: Union[float, str] = None
    is_active: Union[bool, str] = None
    created_at__gte: Union[datetime, str] = None
    created_at__lte: Union[datetime, str] = None

    @validator(
                "name__icontains",
                "exchange_rate__gte",
                "exchange_rate__lte",
                "is_active",
                "created_at__gte",
                "created_at__lte"
    )
    def validate_str(cls, v):
        if v == "" or v == 'None':
            return None
        else:
            return v
