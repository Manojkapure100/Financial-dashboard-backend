import requests
from app.core.dbModels import ApiUsageLimit, Instrument
from app.core.logger import logger
from sqlalchemy.orm import Session
from SmartApi.smartConnect import SmartConnect
import pyotp
from app.helpers.helpers import BaseAPI, externalAPI
from dotenv import load_dotenv
import os

load_dotenv()

class AngleOneAPI(BaseAPI):
    
    def __init__(self, session: Session):
        self.apiName: str = externalAPI.MarketFeedAPI
        self.apiDetail: ApiUsageLimit = ApiUsageLimit()
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
            
            # Convert batch data to ORM objects
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

        # Close the session after all insertions
        session.close()
        print("Batch insertion complete!")

        # Example: Filtering for Nifty options
        # nifty_options = [i for i in instrument_list if "NIFTY" in i['tradingsymbol']]

        # global accessToken, smart_Api
        # if accessToken in (None, ''):
        #     self.getAccessToken(session)
        # # instruments = smart_Api.get_instruments()
        # # return instruments
        # smart_Api.getMarketData('FULL')
        # logger.info(dir(smart_Api))
        # return None
        
    def getStockPrice(self, session: Session, symbol: str):
        stock = session.query(Instrument).filter(
            Instrument.Name == symbol,
            Instrument.ExchangeSegment == 'NSE'
        ).first()
        if stock and stock.Token:
            exchangeToken = {
                "NSE":[stock.Token]
            }
            stockPrice = self.smart_Api.getMarketData('FULL', exchangeToken)
            self.updateCurrentUsage(session)
            return stockPrice
        else:
            raise Exception(f"Investment instrument {symbol} Not found")
        