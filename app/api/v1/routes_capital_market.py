"""
nselib API routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dbModels import Stock
from app.helpers.financialModelingPrepHelper import FinancialModelingPrepAPI
from app.helpers.helpers import send_response, MaxDaysForInterval
from app.helpers.nseApiHelper import NseApi
from app.helpers.indiaApiHelper import IndiaApi
from app.helpers.angleOneApiHelper import AngleOneAPI
from app.core.logger import logger
from app.core.requestResponseModel import getStockPriceListRequest


router = APIRouter(prefix="/api/v1/capitalmarket", tags=["capitalmarket"])

@router.get("/")
async def get_capitalmarket_status():
    """Get capitalmarket status"""
    return {"status": "ok"}

@router.get("/intervals")
async def get_intervals():
    try:
        response = {"intervals": MaxDaysForInterval.list_intervals_with_values()}
        return send_response(status_code=200, body=response)
    except Exception as ex:
        return send_response(status_code=500, message=str(ex))

@router.get("/stock")
async def func(session: Session = Depends(get_db)):
    try:
        nseApiHelper = NseApi()
        # stocks = nseApiHelper.getAllStockData(session)
        stocks = nseApiHelper.getAllStockDataFromAPI()
        return send_response(status_code=200, body=stocks)
    except Exception as ex:
        return send_response(status_code=500, message=str(ex))
    
@router.get("/stock/{companySymbol}")
async def func(companySymbol: str, session: Session = Depends(get_db)):
    indiaApiHelper = IndiaApi(session)
    stock: Stock | None = (
        session.query(Stock)
        .filter(Stock.Symbol == companySymbol)
        .first()
    )

    if not stock.Id:
        return send_response(status_code=400, message='No data found, please check your request')

    if stock.Info:
        return send_response(status_code=200, body=stock)

    logger.info(f"Info of {companySymbol} is not available")
    new_stock = indiaApiHelper.getStockInfo(session, stock)

    if new_stock.Id:
        return send_response(status_code=200, body=new_stock)
    else:
        return send_response(status_code=500, message='Error while fetching stock information')

@router.get("/stock/{companySymbol}/description")
async def func(companySymbol: str, session: Session = Depends(get_db)):
    try:
        indiaApiHelper = IndiaApi(session)
        stock: Stock | None = (
            session.query(Stock)
            .filter(Stock.Symbol == companySymbol)
            .first()
        )
        if not stock.Id:
            return send_response(status_code=400, message=f"No Stock found with symbol {companySymbol}")
        
        response = None
        if stock.Info:
            response = indiaApiHelper.getCompanyDescription(stock)
        else:
            new_stock = indiaApiHelper.getStockInfo(session, stock)
            response = indiaApiHelper.getCompanyDescription(new_stock)
            
        return send_response(status_code=200, body=response)
    except Exception as ex:
        logger.error(str(ex))
        return send_response(status_code=500, message=str(ex))

@router.get("/stock/{companySymbol}/financialRatio")
async def func(companySymbol: str, session: Session = Depends(get_db)):
    try:
        indiaApiHelper = IndiaApi(session)
        stock: Stock | None = (
            session.query(Stock)
            .filter(Stock.Symbol == companySymbol)
            .first()
        )
        if not stock.Id:
            return send_response(status_code=400, message=f"No Stock found with symbol {companySymbol}")
        
        response = None
        if stock.Info:
            response = indiaApiHelper.getStockFinancialRatio(stock)
        else:
            new_stock = indiaApiHelper.getStockInfo(session, stock)
            response = indiaApiHelper.getStockFinancialRatio(new_stock)
            
        return send_response(status_code=200, body=response)
    except Exception as ex:
        logger.error(str(ex))
        return send_response(status_code=500, message=str(ex))

@router.get("/stock/{companySymbol}/currentPriceAndPersentage")
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
    
@router.get("/stock/{companySymbol}/similar")
async def getSimilarStockList(companySymbol: str, session: Session = Depends(get_db)):
    try:
       financialModelingPrepAPIHelper = FinancialModelingPrepAPI(session)
       response = financialModelingPrepAPIHelper.getSimilarStocks(session, companySymbol)
       return send_response(status_code=200, body=response) 
    except Exception as ex:
        return send_response(status_code=500, message=str(ex))