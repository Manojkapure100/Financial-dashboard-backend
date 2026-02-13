"""
nselib API routes
"""

from fastapi import APIRouter, Depends
from nselib import capital_market
from pandas import DataFrame
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dbModels import Stock
from app.helpers.nseApiHelper import NseApi
from app.helpers.indiaApiHelper import IndiaApi
from app.core.logger import logger

router = APIRouter(prefix="/api/v1/capitalmarket", tags=["capitalmarket"])

@router.get("/")
async def get_capitalmarket_status():
    """Get capitalmarket status"""
    return {"status": "ok"}

@router.get("/company")
async def func(session: Session = Depends(get_db)):
    try:
        nseApiHelper = NseApi()
        # stocks = nseApiHelper.getAllStockData(session)
        stocks = nseApiHelper.getAllStockDataFromAPI()
        return {
            "status": "success",
            "data": stocks
        }
    except Exception as ex:
        return {
            "status": "failed",
            "reason": ex
        }
    
@router.get("/company/{companySymbol}")
async def func(companySymbol: str, session: Session = Depends(get_db)):
    indiaApiHelper = IndiaApi(session)
    stock: Stock | None = (
        session.query(Stock)
        .filter(Stock.Symbol == companySymbol)
        .first()
    )

    if not stock:
        return {
            "status": "Success",
            "reason": "No data found, please check your request"
        }

    if stock.Info:
        return {
            "status": "Success",
            "data": stock
        }

    logger.info(f"Info of {companySymbol} is not available")
    new_stock = indiaApiHelper.getStockInfo(session, stock)

    return {
        "status": "Success" if new_stock else "Failed",
        "data": new_stock or []
    }
