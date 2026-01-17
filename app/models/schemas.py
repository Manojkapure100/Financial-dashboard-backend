"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StockData(BaseModel):
    """Stock data schema"""
    symbol: str
    price: float
    volume: int
    timestamp: datetime


class BacktestRequest(BaseModel):
    """Backtest request schema"""
    symbol: str
    start_date: datetime
    end_date: datetime
    strategy: str


class BacktestResponse(BaseModel):
    """Backtest response schema"""
    returns: float
    sharpe_ratio: float
    max_drawdown: float
    trades: int
