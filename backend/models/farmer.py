"""
Farmer data models for Water Futures AI
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class WeatherData(BaseModel):
    """Weather data for a specific location"""
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    precipitation: float = Field(..., description="Precipitation in mm")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    drought_index: Optional[float] = Field(None, description="Palmer Drought Severity Index")
    soil_moisture: Optional[float] = Field(None, description="Soil moisture percentage")
    evapotranspiration: Optional[float] = Field(None, description="ET rate in mm/day")
    forecast_days: Optional[List[Dict[str, Any]]] = Field(None, description="Weather forecast")
    timestamp: datetime = Field(default_factory=datetime.now)

class FarmLocation(BaseModel):
    """Farm location details"""
    zip_code: str = Field(..., description="Farm ZIP code")
    city: Optional[str] = None
    county: Optional[str] = None
    state: str = Field(default="CA", description="State code")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_ft: Optional[float] = None
    water_district: Optional[str] = None
    groundwater_basin: Optional[str] = None

class CropData(BaseModel):
    """Crop information for a farm"""
    crop_type: str = Field(..., description="Type of crop")
    acres: float = Field(..., description="Acres planted")
    water_usage_per_acre: float = Field(..., description="Acre-feet of water per acre")
    planting_date: Optional[datetime] = None
    expected_harvest_date: Optional[datetime] = None
    expected_yield: Optional[float] = None
    irrigation_method: Optional[str] = None

class WaterRights(BaseModel):
    """Water rights and allocations"""
    surface_water_rights: Optional[float] = Field(None, description="Surface water rights in acre-feet")
    groundwater_rights: Optional[float] = Field(None, description="Groundwater rights in acre-feet")
    current_allocation_pct: Optional[float] = Field(None, description="Current allocation percentage")
    water_bank_credits: Optional[float] = Field(None, description="Water bank credits in acre-feet")
    
class Farmer(BaseModel):
    """Complete farmer profile"""
    farmer_id: str = Field(..., description="Unique farmer identifier")
    name: str = Field(..., description="Farmer or farm name")
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Location data
    location: FarmLocation
    
    # Farm details
    total_acres: float = Field(..., description="Total farm acreage")
    irrigated_acres: float = Field(..., description="Irrigated acreage")
    crops: List[CropData] = Field(default_factory=list)
    
    # Water data
    water_rights: Optional[WaterRights] = None
    annual_water_usage: Optional[float] = Field(None, description="Annual water usage in acre-feet")
    water_source_mix: Optional[Dict[str, float]] = Field(None, description="Percentage mix of water sources")
    
    # Financial data
    subsidy_eligible: bool = Field(default=True)
    subsidy_history: List[Dict[str, Any]] = Field(default_factory=list)
    water_futures_positions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Weather and environmental data
    current_weather: Optional[WeatherData] = None
    drought_severity: Optional[int] = Field(None, ge=0, le=5, description="Drought severity 0-5")
    water_stress_level: Optional[str] = Field(None, description="Low, Medium, High, Extreme")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FarmerContext(BaseModel):
    """Context for farmer interactions"""
    farmer_id: str
    location: FarmLocation
    current_weather: Optional[WeatherData] = None
    drought_severity: Optional[int] = None
    recent_trades: List[Dict[str, Any]] = Field(default_factory=list)
    active_subsidies: List[Dict[str, Any]] = Field(default_factory=list)
    agent_mode_enabled: bool = Field(default=False)
    
class WeatherUpdateRequest(BaseModel):
    """Request to update weather data"""
    zip_code: str
    weather_data: Optional[WeatherData] = None
    fetch_latest: bool = Field(default=True, description="Fetch latest weather from API")
    include_forecast: bool = Field(default=True, description="Include weather forecast")
    
class SubsidyEligibilityRequest(BaseModel):
    """Request to check subsidy eligibility"""
    farmer_id: str
    zip_code: str
    drought_severity: Optional[int] = None
    acres_affected: Optional[float] = None
    crop_types: Optional[List[str]] = None
    check_federal: bool = Field(default=True)
    check_state: bool = Field(default=True)
    check_local: bool = Field(default=True)