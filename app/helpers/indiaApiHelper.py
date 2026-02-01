from datetime import datetime
import requests
from app.core.dbModels import Stock, ApiUsageLimit
from app.core.logger import logger
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

class IndiaApi:
    _apiName: str = 'indianAPI'
    _apiDetail: ApiUsageLimit = ApiUsageLimit()
    
    def getApiKey(self, session: Session):
        result = session.query(ApiUsageLimit).filter(
            ApiUsageLimit.ApiName == self._apiName
        ).first()
        
        if result:
            self._apiDetail = result
            logger.info(f"Fetched API key for {result.ApiName}, current usage [{result.CurrentUsage}/{result.MaxLimit}]")
        else:
            errorMessage = f"No API key found for {self._apiName}"
            logger.error(errorMessage)
            raise Exception(errorMessage)
    
    def getStockInfo(self, session: Session, stock: Stock):
        try:
            if not self._apiDetail.ApiKey:
                self.getApiKey(session)
                
            remainingAPIHit: int = int(self._apiDetail.MaxLimit) - int(self._apiDetail.CurrentUsage)
            if remainingAPIHit <= 10:
                logger.error(f"{self._apiName} API Limit about to exceed {remainingAPIHit}, stopping...")
                return None
            elif remainingAPIHit < 50:
                logger.warning(f"{self._apiName} API Limit remain only {remainingAPIHit - 1}, we will stop hitting once it remain 10")
            else:
                logger.info(f"{self._apiName} API Limit remain {remainingAPIHit - 1}")
                
            logger.info(f"fetching info of {stock.FullName}")
             
            url = f"https://{self._apiDetail.ApiBaseUrl}/stock"
            querystring = {"name": stock.Symbol}
            headers = { 'X-Api-Key': self._apiDetail.ApiKey }
            responseFromAPI = requests.get(url, headers=headers, params=querystring)
            
            if not responseFromAPI.ok:
                logger.error(f"Error response: {responseFromAPI.status_code}: {responseFromAPI.text}")
                return None
            
            logger.info(f"Successfully fetched")
            stock.Info = responseFromAPI.json()
            session.flush()
            
            apiToBeUpdate = session.query(ApiUsageLimit).filter(ApiUsageLimit.ApiName == self._apiName).first()
            apiToBeUpdate.CurrentUsage = apiToBeUpdate.CurrentUsage + 1
            apiToBeUpdate.TmStamp = datetime.now()
            self._apiDetail = apiToBeUpdate
            session.flush()
            
            session.commit()
            logger.info(f"Saved info into DB")
            return stock
        except Exception as ex:
            logger.error(f"Error in getStockInfo: {ex}")
        
        