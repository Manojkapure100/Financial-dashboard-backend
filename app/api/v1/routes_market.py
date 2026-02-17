from typing import List
from fastapi import APIRouter, Depends
from app.core.requestResponseModel import getStockPriceListRequest
from app.helpers.angleOneApiHelper import AngleOneAPI
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.helpers.helpers import MaxDaysForInterval, send_response

router = APIRouter(prefix="/api/v1/market", tags=["market"])

@router.get("/")
async def getMarketData(session: Session = Depends(get_db)):
    angleOneApiHelper = AngleOneAPI(session)
    # result = angleOneApiHelper.getAllStockData(session)
    return {
        "Status": "Success",
        "Result": True #result
    }

@router.get("/stock/{companySymbol}")
async def getStockPrice(companySymbol: str, session: Session = Depends(get_db)):
    try:
        angleOneApiHelper = AngleOneAPI(session)
        response = angleOneApiHelper.getStockPrice(session, companySymbol)
        return send_response(status_code=200, body=response)
    except Exception as ex:
        return send_response(status_code=500, message=str(ex))

@router.post("/stock/priceList")
async def getStockPriceList(request: getStockPriceListRequest, session: Session = Depends(get_db)):
    try:
        angleOneApiHelper = AngleOneAPI(session)
        response = angleOneApiHelper.getStockPriceList(session, request)
        return send_response(status_code=200, body=response)
    except Exception as ex:
        return send_response(status_code=500, message=str(ex))
    
@router.get("/intervals")
async def get_intervals():
    try:
        response = {"intervals": MaxDaysForInterval.list_intervals_with_values()}
        return send_response(status_code=200, body=response)
    except Exception as ex:
        return send_response(status_code=500, message=str(ex))