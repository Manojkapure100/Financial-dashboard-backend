"""
Main application entry point
"""

from fastapi import FastAPI
from app.api.v1 import routes_backtest, routes_screener, routes_market

app = FastAPI(title="Financial Dashboard Backend")

# Include routers
app.include_router(routes_backtest.router)
app.include_router(routes_screener.router)
app.include_router(routes_market.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Financial Dashboard API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
