from typing import List, Optional
from datetime import datetime, timedelta
from services.water_futures_service import WaterFuturesService
from services.database import get_db

class WaterFuturesController:
    def __init__(self):
        self.service = WaterFuturesService()
    
    async def get_current_prices(self):
        return await self.service.get_current_prices()
    
    async def get_nasdaq_water_index(self):
        return await self.service.get_nasdaq_water_index()
    
    async def get_historical_prices(
        self,
        contract_code: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        interval: str
    ):
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        return await self.service.get_historical_data(
            contract_code, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
    
    async def list_available_contracts(self):
        return await self.service.get_available_contracts()
    
    async def refresh_market_data(self):
        return await self.service.refresh_all_market_data()