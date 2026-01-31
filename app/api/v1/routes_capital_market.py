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
from app.core.apiHelper import ApiHelper

router = APIRouter(prefix="/api/v1/capitalmarket", tags=["capitalmarket"])
apiHelper = ApiHelper()

@router.get("/")
async def get_capitalmarket_status():
    """Get capitalmarket status"""
    return {"status": "ok"}

@router.get("/all")
async def func(session: Session = Depends(get_db)):
    try:
        stocks = apiHelper.getAllStockData(session)
        return {
            "status": "success",
            "data": stocks
        }
    except Exception as ex:
        return {
            "status": "failed",
            "reason": ex
        }
    
@router.get("/company/{companyName}")
async def test(companyName: str, session: Session = Depends(get_db)):
    return session.query(Stock).all()