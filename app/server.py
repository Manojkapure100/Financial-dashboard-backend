"""
Main application entry point
"""

from fastapi import FastAPI
from app.api.v1 import routes_market, routes_capital_market
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dbModels import Stock
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Financial Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:4200/",
        "https://manojkapure100.github.io",
        "https://manojkapure100.github.io/",
        "https://manojkapure100.github.io/Financial-dashboard",
        "https://manojkapure100.github.io/Financial-dashboard/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_market.router)
app.include_router(routes_capital_market.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Financial Dashboard API"}

@app.get("/test")
async def test(session: Session = Depends(get_db)):
    return session.query(Stock).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
