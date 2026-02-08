from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from typing import Any
import pandas as pd
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.core.dbModels import ApiUsageLimit
from enum import Enum

class BaseAPI:
    def updateCurrentUsage(self, session: Session):
        result: ApiUsageLimit = session.query(ApiUsageLimit).filter(
                ApiUsageLimit.ApiName == self.apiName
        ).first()
        result.CurrentUsage += 1
        session.commit()

    def getApiKey(self, session: Session):
        result: ApiUsageLimit = session.query(ApiUsageLimit).filter(
            ApiUsageLimit.ApiName == self.apiName
        ).first()
        
        if result: 
            self.apiDetail = result
            logger.info(f"Fetched API key for {result.ApiName}, current usage [{result.CurrentUsage}/{result.MaxLimit}]")
            return self.apiDetail.ApiKey
        else:
            errorMessage = f"No API key found for {self.apiName}"
            logger.error(errorMessage)
            raise Exception(errorMessage)
        
class externalAPI(Enum):
    IndiaAPI = 'indianAPI'
    MarketFeedAPI = 'MarketFeedAPI'
    NSEAPI = ''
    HistoricalAPI = ''

def send_response(
    *,
    status_code: int,
    body: Any = None,
    message: str | None = None
):

    def prepare_body(body):
        if body is None:
            return {"body": None}
        elif isinstance(body, pd.DataFrame):
            return {"body": body.to_dict(orient="records")}
        else:
            # already dict / list / other serializable type
            return {"body": body}

    body = prepare_body(body)

    if message:
        body["message"] = message

    return JSONResponse(
        status_code=status_code,
        content=body
    )

def get_date_range(days: int) -> tuple:
    """Get date range for the last N days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency"""
    return f"₹{value:.{decimals}f}"
