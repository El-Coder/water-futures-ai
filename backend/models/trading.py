from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, JSON, Enum
from .base import BaseModel
from datetime import datetime
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderType(enum.Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class Trade(BaseModel):
    __tablename__ = "trades"
    
    order_id = Column(String(100), unique=True, nullable=False)
    contract_code = Column(String(50), nullable=False, index=True)
    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float)
    executed_price = Column(Float)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    filled_quantity = Column(Integer, default=0)
    commission = Column(Float, default=0.0)
    executed_at = Column(DateTime(timezone=True))
    metadata = Column(JSON, default={})
    
class Portfolio(BaseModel):
    __tablename__ = "portfolios"
    
    portfolio_name = Column(String(200), nullable=False, unique=True)
    total_value = Column(Float, nullable=False, default=0.0)
    cash_balance = Column(Float, nullable=False, default=0.0)
    positions = Column(JSON, default={})
    performance_metrics = Column(JSON, default={})
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
class Position(BaseModel):
    __tablename__ = "positions"
    
    portfolio_id = Column(Integer, nullable=False)
    contract_code = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
class TradingStrategy(BaseModel):
    __tablename__ = "trading_strategies"
    
    strategy_name = Column(String(200), nullable=False, unique=True)
    strategy_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    performance_stats = Column(JSON, default={})
    last_signal = Column(DateTime(timezone=True))
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    average_return = Column(Float)