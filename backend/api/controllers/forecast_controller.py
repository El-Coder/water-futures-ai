from typing import Optional
from datetime import datetime
from services.forecast_service import ForecastService
from services.ml_service import MLService

class ForecastController:
    def __init__(self):
        self.forecast_service = ForecastService()
        self.ml_service = MLService()
    
    async def generate_forecast(
        self,
        contract_code: str,
        horizon_days: int,
        include_embeddings: bool,
        include_news_sentiment: bool
    ):
        # Use the forecast service predict method directly
        prediction = await self.forecast_service.predict(
            contract_code=contract_code,
            horizon_days=horizon_days
        )
        
        return {
            "contract_code": contract_code,
            "current_price": prediction.get("current_price", 508),
            "predicted_prices": prediction.get("predicted_prices", []),
            "confidence_intervals": prediction.get("confidence_intervals", []),
            "model_confidence": prediction.get("confidence", 0.75),
            "factors": prediction.get("contributing_factors", {})
        }
    
    async def get_active_signals(self):
        return await self.forecast_service.get_trading_signals()
    
    async def get_model_performance(self, contract_code: str):
        return await self.ml_service.get_performance_metrics(contract_code)
    
    async def run_backtest(
        self,
        contract_code: str,
        start_date: datetime,
        end_date: datetime
    ):
        return await self.ml_service.backtest_strategy(
            contract_code,
            start_date,
            end_date
        )