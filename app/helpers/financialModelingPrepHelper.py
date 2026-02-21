from datetime import datetime
import requests
from app.core.dbModels import ApiUsageLimit, Instrument, Stock
from app.core.logger import logger
from sqlalchemy.orm import Session
from SmartApi.smartConnect import SmartConnect
import pyotp
from app.core.requestResponseModel import getStockPriceListRequest
from app.helpers.helpers import BaseAPI, MaxDaysForInterval, externalAPI, retry_on_failure
from dotenv import load_dotenv
import os
from requests.exceptions import RequestException

load_dotenv()

class FinancialModelingPrepAPI(BaseAPI):
    def __init__(self, session: Session):
        self.apiName = externalAPI.FinancialModelingPrepAPI.value
        self.getApiKey(session)

    def getSimilarStocks(self, session:Session, symbol: str):
        try:
            stock = session.query(Stock).filter(
                Stock.Symbol == symbol,
            ).first()
            if stock and stock.Id:
                stockSymbol = f'{symbol}.ns'
                url = f"https://{self.apiDetail.ApiBaseUrl}/stock-peers"
                querystring = {"symbol": stockSymbol, "apikey": self.apiDetail.ApiKey}
                responseFromAPI = requests.get(url, params=querystring)

                if not responseFromAPI.ok:
                    logger.error(f"Error response: {responseFromAPI.status_code}: {responseFromAPI.text}")
                    return None
                
                apiToBeUpdate = session.query(ApiUsageLimit).filter(ApiUsageLimit.ApiName == self.apiName).first()
                apiToBeUpdate.CurrentUsage = apiToBeUpdate.CurrentUsage + 1
                apiToBeUpdate.TmStamp = datetime.now()
                self.apiDetail = apiToBeUpdate
                session.flush()

                session.commit()
                info = responseFromAPI.json()
                return info
            else:
                raise Exception(f'No Stock found for {symbol}')
        except Exception as ex:
            logger.error(f"Error in getSimilarStocks: {ex}")