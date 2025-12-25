from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CryptoDataBase(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class CryptoData(CryptoDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StockDataBase(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class StockData(StockDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
