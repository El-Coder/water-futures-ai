from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime

class WaterFuture(BaseModel):
    __tablename__ = "water_futures"
    
    contract_code = Column(String(50), unique=True, nullable=False, index=True)
    contract_month = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, default=0)
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)
    close = Column(Float)
    settlement_price = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
class WaterIndex(BaseModel):
    __tablename__ = "water_indices"
    
    index_name = Column(String(100), nullable=False)
    index_value = Column(Float, nullable=False)
    region = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    meta_data = Column(JSON, default={})
    
class HistoricalPrice(BaseModel):
    __tablename__ = "historical_prices"
    
    contract_code = Column(String(50), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Integer)
    settlement_price = Column(Float)
    open_interest = Column(Integer)
    
class TradingSignal(BaseModel):
    __tablename__ = "trading_signals"
    
    contract_code = Column(String(50), nullable=False, index=True)
    signal_type = Column(String(20), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    predicted_price = Column(Float)
    current_price = Column(Float)
    reasoning = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    generated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)