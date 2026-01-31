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
