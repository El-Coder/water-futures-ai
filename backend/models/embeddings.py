from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, ARRAY
try:
    from sqlalchemy.dialects.postgresql import VECTOR
except ImportError:
    # Fallback for environments without pgvector
    VECTOR = String
from .base import BaseModel
from datetime import datetime

class SatelliteEmbedding(BaseModel):
    __tablename__ = "satellite_embeddings"
    
    location_id = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    embedding = Column(VECTOR(768))  # Using pgvector for embeddings
    resolution = Column(String(20), default="10m")
    capture_date = Column(DateTime(timezone=True), nullable=False)
    metadata = Column(JSON, default={})
    
class PDFMEmbedding(BaseModel):
    __tablename__ = "pdfm_embeddings"
    
    location_id = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    population_density = Column(Float)
    demographic_embedding = Column(VECTOR(512))  # Population dynamics embedding
    economic_indicators = Column(JSON, default={})
    water_usage_estimate = Column(Float)  # Estimated water usage in the area
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
class RegionAnalysis(BaseModel):
    __tablename__ = "region_analyses"
    
    region_name = Column(String(200), nullable=False)
    county = Column(String(100))
    state = Column(String(50), default="California")
    total_area_sqkm = Column(Float)
    agricultural_area_sqkm = Column(Float)
    urban_area_sqkm = Column(Float)
    water_sources = Column(JSON, default=[])
    drought_severity = Column(Integer)  # 0-5 scale
    precipitation_mm = Column(Float)
    temperature_celsius = Column(Float)
    combined_embedding = Column(VECTOR(1024))  # Combined satellite + PDFM
    analysis_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    predictions = Column(JSON, default={})