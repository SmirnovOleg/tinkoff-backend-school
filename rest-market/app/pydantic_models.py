from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, validator


class NewCryptoRequestBodyModel(BaseModel):
    crypto_name: str
    sale_price: Decimal
    purchase_price: Decimal

    @validator('sale_price', 'purchase_price')
    def prices_must_be_positive(cls, price: Decimal) -> Decimal:
        if price <= 0:
            raise ValueError('must be positive')
        return price


class CryptoTransactionRequestBodyModel(BaseModel):
    utc_datetime: Optional[datetime]
    login: str
    crypto_name: str
    amount: Decimal

    @validator('amount')
    def buy_amount_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError('must be positive')
        return value


class LoginRequestBodyModel(BaseModel):
    login: str


class PaginationQueryModel(BaseModel):
    page: int

    @validator('page')
    def page_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError('must be positive')
        return value
