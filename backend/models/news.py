from sqlalchemy import Column, String, Text, Float, DateTime, Boolean, JSON
from .base import BaseModel
from datetime import datetime

class NewsArticle(BaseModel):
    __tablename__ = "news_articles"
    
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False)
    source = Column(String(200), nullable=False)
    author = Column(String(200))
    content = Column(Text)
    summary = Column(Text)
    published_at = Column(DateTime(timezone=True), nullable=False)
    relevance_score = Column(Float, default=0.0)
    sentiment_score = Column(Float)  # -1 to 1
    categories = Column(JSON, default=[])
    keywords = Column(JSON, default=[])
    locations_mentioned = Column(JSON, default=[])
    is_california_related = Column(Boolean, default=False)
    is_water_related = Column(Boolean, default=False)
    
class MarketInsight(BaseModel):
    __tablename__ = "market_insights"
    
    insight_type = Column(String(50), nullable=False)  # NEWS, ANALYSIS, ALERT
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    impact_level = Column(String(20))  # HIGH, MEDIUM, LOW
    affected_regions = Column(JSON, default=[])
    price_impact_estimate = Column(Float)
    confidence_level = Column(Float)
    source_articles = Column(JSON, default=[])
    generated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime(timezone=True))
    
class WaterEvent(BaseModel):
    __tablename__ = "water_events"
    
    event_type = Column(String(100), nullable=False)  # DROUGHT, FLOOD, POLICY_CHANGE, etc
    title = Column(String(500), nullable=False)
    description = Column(Text)
    severity = Column(Integer)  # 1-10 scale
    affected_counties = Column(JSON, default=[])
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    estimated_impact = Column(JSON, default={})
    data_sources = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)