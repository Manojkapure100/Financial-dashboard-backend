from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from typing import Any
import pandas as pd
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.core.dbModels import ApiUsageLimit
from enum import Enum
import time
from functools import wraps
from requests.exceptions import RequestException

class BaseAPI:
    apiName: str = ''
    apiDetail: ApiUsageLimit = ApiUsageLimit() 
    
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
    
class MaxDaysForInterval(Enum):
    ONE_MINUTE = 30
    THREE_MINUTE = 60
    FIVE_MINUTE = 100
    TEN_MINUTE = 100
    FIFTEEN_MINUTE = 200
    THIRTY_MINUTE = 200
    ONE_HOUR = 400
    ONE_DAY = 2000

    @classmethod
    def list_intervals(cls):
        return [e.name for e in cls]
    
    @classmethod
    def list_intervals_with_values(cls):
        return [{"name": e.name, "value": e.value} for e in cls]

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

def retry_on_failure(max_retries=3, initial_delay=2, backoff_factor=2):
    """
    Decorator to add retry logic to any function that may fail temporarily (like network requests).
    - max_retries: Maximum number of retries before giving up.
    - initial_delay: Initial delay in seconds before the first retry.
    - backoff_factor: Multiplier to increase delay between retries (exponential backoff).
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_retries:
                try:
                    # Try to execute the function
                    return func(*args, **kwargs)
                except RequestException as e:
                    attempt += 1
                    logger.error(f"Error in function {func.__name__}: {e}. Attempt {attempt}/{max_retries}")
                    
                    if attempt < max_retries:
                        # Exponential backoff (2^n where n is attempt-1)
                        wait_time = initial_delay * (backoff_factor ** (attempt - 1))
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries reached for {func.__name__}. Failing after {max_retries} attempts.")
                        raise Exception(f"Failed after {max_retries} retries: {e}")
        return wrapper
    return decorator

