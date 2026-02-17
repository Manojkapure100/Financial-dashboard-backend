"""
Main application entry point
"""

from fastapi import FastAPI, Request
from sqlalchemy import text
from app.api.v1 import routes_market, routes_capital_market
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dbModels import Stock
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger

app = FastAPI(title="Financial Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",       # local dev
        "https://manojkapure100.github.io",  # GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_origin(request, call_next):
    logger.info(f"Origin header: {request.headers.get("origin")}")
    response = await call_next(request)
    return response

# Include routers
app.include_router(routes_market.router)
app.include_router(routes_capital_market.router)


@app.get("/")
async def root(session: Session = Depends(get_db)):
    try:
        result = session.execute(text('select 1'))
        working = result.fetchone()[0]
        return {"message": f"Welcome to Financial Dashboard API, database {'not ' if not working else ''}working"}
    except Exception as ex:
        return {"message": f"Welcome to Financial Dashboard API, database not working"}

@app.get("/test")
async def test(session: Session = Depends(get_db)):
    return session.query(Stock).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
