from datetime import datetime
from pandas import DataFrame
from sqlalchemy.orm import Session
from app.core.dbModels import Stock
from app.core.logger import logger
from nselib import capital_market

class NseApi:
    def getStockInfo(self, session: Session, stock: Stock):
        logger.info(f"fetching info of {stock.FullName}")
        
    def getAllStockDataFromAPI(self):
        stocks: DataFrame = capital_market.equity_list()
        stockRecords = stocks.to_dict(orient="records")
        return stockRecords
        
    def getAllStockData(self, session: Session):
        stocks = session.query(Stock.Symbol, Stock.FullName, Stock.Info).all()
        if stocks:
            logger.info("Responsing from db")
            return [
                {"Symbol": stock.Symbol, "FllName": stock.FullName, "Info": stock.Info}
                for stock in stocks
            ]
        else:
            stocksToAdd: DataFrame = capital_market.equity_list()[["NAME OF COMPANY", "SYMBOL"]]
            self.storeAllEquityInTable(session, stocksToAdd)
            stocks = session.query(Stock.Symbol, Stock.FullName, Stock.Info).all()            
            if stocks:
                return [
                    {"Symbol": stock.Symbol, "FllName": stock.FullName, "Info": stock.Info}
                    for stock in stocks
                ]
            else:
                []
    
    def storeAllEquityInTable(self, session: Session, stocks: DataFrame):
        try:
            stockRenamed = stocks.rename(columns={
                "NAME OF COMPANY": "FullName",
                "SYMBOL": "Symbol"
            })
            stockRenamed["DateCreated"] = datetime.now()
            stockRenamed["TmStamp"] = datetime.now()
            stockRecords = stockRenamed.to_dict(orient="records")
            stockObjects = [Stock(**stockRecord) for stockRecord in stockRecords]
            session.add_all(stockObjects)
            session.commit()
            logger.info(f"{len(stockRecords)} stocks added successfullly")
        except Exception as ex:
            logger.error(f"Error storeAllEquityInTable %s", ex)
            raise Exception("Something went wrong on while Adding stocks")
