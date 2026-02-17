from datetime import datetime
import requests
from app.core.dbModels import Stock, ApiUsageLimit
from app.core.logger import logger
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.helpers.helpers import BaseAPI, externalAPI

class IndiaApi(BaseAPI):
    def __init__(self, session: Session):
        self.apiName = externalAPI.IndiaAPI.value
        self.getApiKey(session)
    
    def getStockInfo(self, session: Session, stock: Stock):
        try:    
            remainingAPIHit: int = int(self.apiDetail.MaxLimit) - int(self.apiDetail.CurrentUsage)
            if remainingAPIHit <= 10:
                logger.error(f"{self.apiName} API Limit about to exceed {remainingAPIHit}, stopping...")
                return None
            elif remainingAPIHit < 50:
                logger.warning(f"{self.apiName} API Limit remain only {remainingAPIHit - 1}, we will stop hitting once it remain 10")
            else:
                logger.info(f"{self.apiName} API Limit remain {remainingAPIHit - 1}")
                
            logger.info(f"fetching info of {stock.FullName}")
             
            url = f"https://{self.apiDetail.ApiBaseUrl}/stock"
            querystring = {"name": stock.Symbol}
            headers = { 'X-Api-Key': self.apiDetail.ApiKey }
            responseFromAPI = requests.get(url, headers=headers, params=querystring)
            
            if not responseFromAPI.ok:
                logger.error(f"Error response: {responseFromAPI.status_code}: {responseFromAPI.text}")
                return None
            
            logger.info(f"Successfully fetched")
            stock.Info = responseFromAPI.json()
            session.flush()
            
            apiToBeUpdate = session.query(ApiUsageLimit).filter(ApiUsageLimit.ApiName == self.apiName).first()
            apiToBeUpdate.CurrentUsage = apiToBeUpdate.CurrentUsage + 1
            apiToBeUpdate.TmStamp = datetime.now()
            self.apiDetail = apiToBeUpdate
            session.flush()
            
            session.commit()
            logger.info(f"Saved info into DB")
            return stock
        except Exception as ex:
            logger.error(f"Error in getStockInfo: {ex}")

    def getCompanyDescription(self, stock: Stock):
        companyDescription = stock.Info.get("companyProfile").get("companyDescription")
        return companyDescription
            
    def getStockFinancialRatio(self, stock: Stock):
        financials: list = stock.Info["financials"]

        if not financials:
            raise Exception(f"No Finaicial ratio found for stock {stock.FullName}")
        
        annualFinancials = []
        for financial in financials:
            if(financial["Type"] != "Annual"):
                continue
            annualFinancials.append(financial)
            
        sorted_financials = sorted(
            annualFinancials,
            key=lambda x: int(x.get("FiscalYear", 0)),
            reverse=True
        )
        
        all_data = [
            {
                "year": f.get("FiscalYear"),
                "ratios": self.calculate_ratios(f)
            }
            for f in sorted_financials
        ]
    
        return all_data
    

    def get_value(self, data_list: list, key: str):
        if not data_list:
            return None

        for item in data_list:
            if item.get("key") == key:
                value = item.get("value")
                try:
                    return float(value) if value is not None else None
                except (TypeError, ValueError):
                    return None

        return None


    def calculate_ratios(self, financial: dict) -> dict:
        stock_map = financial.get("stockFinancialMap", {})

        BAL = stock_map.get("BAL", [])
        INC = stock_map.get("INC", [])
        CAS = stock_map.get("CAS", [])

        # BAL
        totalCurrentAssets = self.get_value(BAL, "TotalCurrentAssets")
        totalCurrentLiabilities = self.get_value(BAL, "TotalCurrentLiabilities")
        inventory = self.get_value(BAL, "TotalInventory")
        cash = self.get_value(BAL, "Cash")
        cashEq = self.get_value(BAL, "CashEquivalents")
        shortInv = self.get_value(BAL, "ShortTermInvestments")
        totalAssets = self.get_value(BAL, "TotalAssets")
        totalEquity = self.get_value(BAL, "TotalEquity")
        totalDebt = self.get_value(BAL, "TotalDebt")

        # INC
        revenue = self.get_value(INC, "TotalRevenue")
        grossProfit = self.get_value(INC, "GrossProfit")
        operatingIncome = self.get_value(INC, "OperatingIncome")
        netIncome = self.get_value(INC, "NetIncome")
        interestExp = self.get_value(INC, "InterestInc(Exp)Net-Non-OpTotal")

        # CAS
        operatingCashFlow = self.get_value(CAS, "CashfromOperatingActivities")
        capex = self.get_value(CAS, "CapitalExpenditures")

        return {
            # Liquidity
            "currentRatio":
                (totalCurrentAssets / totalCurrentLiabilities)
                if totalCurrentAssets and totalCurrentLiabilities else None,

            "quickRatio":
                ((totalCurrentAssets - inventory) / totalCurrentLiabilities)
                if totalCurrentAssets and inventory and totalCurrentLiabilities else None,

            "cashRatio":
                ((cash + cashEq + shortInv) / totalCurrentLiabilities)
                if cash and cashEq and shortInv and totalCurrentLiabilities else None,

            "operatingCashFlowRatio":
                (operatingCashFlow / totalCurrentLiabilities)
                if operatingCashFlow and totalCurrentLiabilities else None,

            # Profitability
            "grossMargin":
                (grossProfit / revenue)
                if grossProfit and revenue else None,

            "operatingMargin":
                (operatingIncome / revenue)
                if operatingIncome and revenue else None,

            "netProfitMargin":
                (netIncome / revenue)
                if netIncome and revenue else None,

            "returnOnAssets":
                (netIncome / totalAssets)
                if netIncome and totalAssets else None,

            "returnOnEquity":
                (netIncome / totalEquity)
                if netIncome and totalEquity else None,

            # Leverage
            "debtToEquity":
                (totalDebt / totalEquity)
                if totalDebt and totalEquity else None,

            "debtToAssets":
                (totalDebt / totalAssets)
                if totalDebt and totalAssets else None,

            "interestCoverage":
                (operatingIncome / abs(interestExp))
                if operatingIncome and interestExp else None,

            # Efficiency / Value
            "assetTurnover":
                (revenue / totalAssets)
                if revenue and totalAssets else None,

            "inventoryTurnover":
                (revenue / inventory)
                if revenue and inventory else None,

            "freeCashFlowMargin":
                ((operatingCashFlow - abs(capex)) / revenue)
                if operatingCashFlow and capex and revenue else None
        }
