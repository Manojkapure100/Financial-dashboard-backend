from datetime import datetime
import requests
from app.core.dbModels import Instrument, Stock
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

class AngleOneAPI(BaseAPI):
    def __init__(self, session: Session):
        self.apiName: str = externalAPI.MarketFeedAPI.value
        self.client_code = os.getenv("CLIENT_CODE")
        self.password = os.getenv("PASSWORD")
        self.totp_token = os.getenv("TOTP_TOKEN")
        self.correlation_id = os.getenv("CORRELATION_ID")
        self.accessToken = None
        self.smart_Api: SmartConnect = SmartConnect()
        self.getApiKey(session)
        self.getAccessToken()
    
    def getAccessToken(self):
        totp = pyotp.TOTP(self.totp_token).now()
        self.smart_Api = SmartConnect(self.apiDetail.ApiKey)
            
        data = self.smart_Api.generateSession(self.client_code, self.password, totp)
        if data['status'] == False:
            logger.error(data)
        self.accessToken = data['data']['jwtToken']
        return [self.accessToken, self.smart_Api]
    
    def getAllStockData(self, session: Session):
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        instrument_list = response.json()
        
        batch_size = 10000  # Insert in batches of 10,000 records
        for i in range(0, len(instrument_list), batch_size):
            batch_data = instrument_list[i:i+batch_size]
            
            instruments_to_add = [
                Instrument(
                    Token=data['token'],
                    Symbol=data['symbol'],
                    Name=data['name'],
                    InstrumentType=data['instrumenttype'],
                    ExchangeSegment=data['exch_seg']
                )
                for data in batch_data
            ]
            session.add_all(instruments_to_add)
            session.commit()
            logger.info(f'{i+batch_size} inserted') 
            session.expunge_all()

        session.close()
        print("Batch insertion complete!")
        
    @retry_on_failure()
    def getStockPrice(self, session: Session, symbol: str):
        stock = session.query(Stock).filter(
            Stock.Symbol == symbol,
        ).first()
        if stock and stock.Token:
            exchangeToken = {
                "NSE":[stock.Token]
            }
            resp = self.smart_Api.getMarketData('FULL', exchangeToken)
            if resp["errorcode"] == 'AB1004':
                raise RequestException("failed with AB1004")
            
            self.updateCurrentUsage(session)
            return resp
        else:
            raise Exception(f"Investment instrument {symbol} Not found")
        
    def getMaxDays(self, interval: str) -> int:
        return MaxDaysForInterval[interval].value
        
    @retry_on_failure()
    def getStockPriceList(self, session: Session, request: getStockPriceListRequest):
        stock = session.query(Stock).filter(
            Stock.Symbol == request.symbol
        ).first()
        if stock and stock.Token:
            dateDiff = datetime.strptime(request.toDate, "%Y-%m-%d %H:%M") - datetime.strptime(request.fromDate, "%Y-%m-%d %H:%M")
            maxDays = self.getMaxDays(request.interval)
            if dateDiff.days > maxDays:
                raise Exception(f"Invalid request for price list of stock {stock.FullName}")
            
            reqParams = {
                "exchange": "NSE",
                "symboltoken": str(stock.Token),
                "interval": request.interval,
                "fromdate":  request.fromDate,
                "todate":  request.toDate
            }
            resp = self.smart_Api.getCandleData(reqParams)
            if resp["errorcode"] == 'AB1004':
                raise RequestException("failed with AB1004")
            elif resp["errorcode"] not in ('',None,""):
                raise Exception("Failed with exception")
            
            self.updateCurrentUsage(session)
            return resp
        else:
            raise Exception(f"Investment instrument {request.symbol} Not found")