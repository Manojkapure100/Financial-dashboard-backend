from datetime import datetime
import requests
from app.core.dbModels import Stock, ApiUsageLimit
from app.core.logger import logger
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.helpers.helpers import BaseAPI, externalAPI

class IndiaApi(BaseAPI):
    def __init__(self, session: Session):
        self.apiName = externalAPI.IndiaAPI.value
        self.getApiKey(session)
    
    def getStockInfo(self, session: Session, stock: Stock):
        try:    
            remainingAPIHit: int = int(self.apiDetail.MaxLimit) - int(self.apiDetail.CurrentUsage)
            if remainingAPIHit <= 10:
                logger.error(f"{self.apiName} API Limit about to exceed {remainingAPIHit}, stopping...")
                return None
            elif remainingAPIHit < 50:
                logger.warning(f"{self.apiName} API Limit remain only {remainingAPIHit - 1}, we will stop hitting once it remain 10")
            else:
                logger.info(f"{self.apiName} API Limit remain {remainingAPIHit - 1}")
                
            logger.info(f"fetching info of {stock.FullName}")
             
            url = f"https://{self.apiDetail.ApiBaseUrl}/stock"
            querystring = {"name": stock.Symbol}
            headers = { 'X-Api-Key': self.apiDetail.ApiKey }
            responseFromAPI = requests.get(url, headers=headers, params=querystring)
            
            if not responseFromAPI.ok:
                logger.error(f"Error response: {responseFromAPI.status_code}: {responseFromAPI.text}")
                return None
            
            logger.info(f"Successfully fetched")
            stock.Info = responseFromAPI.json()
            session.flush()
            
            apiToBeUpdate = session.query(ApiUsageLimit).filter(ApiUsageLimit.ApiName == self.apiName).first()
            apiToBeUpdate.CurrentUsage = apiToBeUpdate.CurrentUsage + 1
            apiToBeUpdate.TmStamp = datetime.now()
            self.apiDetail = apiToBeUpdate
            session.flush()
            
            session.commit()
            logger.info(f"Saved info into DB")
            return stock
        except Exception as ex:
            logger.error(f"Error in getStockInfo: {ex}")
        
        