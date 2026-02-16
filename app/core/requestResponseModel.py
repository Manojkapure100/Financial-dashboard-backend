from datetime import datetime
from pydantic import BaseModel

class getStockPriceListRequest(BaseModel):
    symbol: str
    interval: str
    fromDate: str
    toDate: str
