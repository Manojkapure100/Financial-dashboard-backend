"""
Screener API routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/screener", tags=["screener"])


@router.get("/")
async def get_screener_status():
    """Get screener status"""
    return {"status": "ok"}
