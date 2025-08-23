from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.controllers.embeddings_controller import EmbeddingsController
from pydantic import BaseModel

router = APIRouter()
controller = EmbeddingsController()

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 10.0

class RegionAnalysisResponse(BaseModel):
    region_name: str
    drought_severity: int
    water_usage_estimate: float
    agricultural_impact: dict
    recommendations: List[str]

@router.post("/analyze/location", response_model=RegionAnalysisResponse)
async def analyze_location(request: LocationRequest):
    try:
        return await controller.analyze_location(
            latitude=request.latitude,
            longitude=request.longitude,
            radius_km=request.radius_km
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions")
async def get_analyzed_regions():
    try:
        return await controller.get_all_regions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions/{region_name}")
async def get_region_details(region_name: str):
    try:
        return await controller.get_region_analysis(region_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/satellite/process")
async def process_satellite_data(
    region: str,
    date_range_days: int = Query(default=30)
):
    try:
        return await controller.process_satellite_embeddings(region, date_range_days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdfm/process")
async def process_pdfm_data(region: str):
    try:
        return await controller.process_pdfm_embeddings(region)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drought-map")
async def get_drought_map():
    try:
        return await controller.get_drought_severity_map()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))