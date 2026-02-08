from sqlalchemy import JSON, Column, DateTime, Integer, String
from app.core.database import Base

class Stock(Base):
    __tablename__ = "Stock"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Symbol = Column(String(20), nullable=True)
    FullName = Column(String(100), nullable=True)
    Info = Column(JSON, nullable=True)
    DateCreated = Column(DateTime, nullable=True)
    TmStamp = Column(DateTime, nullable=True)
    Token = Column(Integer, nullable=True)
    
class ApiUsageLimit(Base):
    __tablename__ = "ApiUsageLimit"
    
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ApiName = Column(String(50), nullable=False)
    ApiBaseUrl = Column(String(50), nullable=False)
    CurrentUsage = Column(Integer, nullable=False)
    MaxLimit = Column(Integer, nullable=False)
    ResetInMonth = Column(Integer, nullable=False)
    ApiKey = Column(String(100), nullable=False)
    SecreteKey = Column(String(100), nullable=True)
    DateCreated = Column(DateTime, nullable=True)
    TmStamp = Column(DateTime, nullable=True)
    
class Instrument(Base):
    __tablename__ = "Instrument"
    
    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Token = Column(String(20), nullable=True)
    Symbol = Column(String(20), nullable=False)
    Name = Column(String(100), nullable=False)
    InstrumentType = Column(String(10), nullable=True)
    ExchangeSegment = Column(String(10), nullable=True)
