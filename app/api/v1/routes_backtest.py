"""
Backtest API routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])


@router.get("/")
async def get_backtest_status():
    """Get backtest status"""
    return {"status": "ok"}
