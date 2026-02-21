from fastapi import FastAPI
from sqlalchemy import text
from app.api.v1 import routes_capital_market
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dbModels import Stock
from fastapi.middleware.cors import CORSMiddleware
from app.core.logger import logger
from app.helpers.helpers import send_response

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
app.include_router(routes_capital_market.router)

@app.get("/")
async def root(session: Session = Depends(get_db)):
    try:
        result = session.execute(text('select 1'))
        working = result.fetchone()[0]
        message = f"Welcome to Financial Dashboard API, database {'not ' if not working else ''}working"
        return send_response(status_code=200, body=message)
    except Exception as ex:
        message = f"Welcome to Financial Dashboard API, database not working"
        return send_response(status_code=500, body=message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
