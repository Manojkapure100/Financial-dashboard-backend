"""
Market API routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.get("/")
async def get_market_status():
    """Get market status"""
    return {"status": "ok"}
