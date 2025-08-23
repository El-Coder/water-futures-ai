"""
Forecast Service - Handles price predictions and forecasting
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from services.vertex_ai_service import vertex_ai_service
from services.data_store import data_store

class ForecastService:
    """Service for generating water futures price forecasts"""
    
    def __init__(self):
        self.vertex_ai = vertex_ai_service
        self.data_store = data_store
        
    async def generate_forecast(
        self, 
        contract_code: str,
        horizon_days: int = 7,
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate price forecast for a water futures contract
        """
        # Get historical data
        historical_data = self.data_store.get_historical_prices(contract_code)
        
        # Prepare features for Vertex AI
        features = {
            "contract_code": contract_code,
            "horizon_days": horizon_days,
            "drought_severity": 4,  # Would come from real drought data
            "precipitation": 35,  # mm, would come from weather data
            "region": "Central Valley",
        }
        
        # Add historical prices if available
        if not historical_data.empty and 'close' in historical_data.columns:
            features["current_price"] = float(historical_data['close'].iloc[-1])
            features["historical_prices"] = historical_data['close'].tail(30).tolist()
        else:
            features["current_price"] = 508.0  # Default price
            features["historical_prices"] = []
        
        # Get prediction from Vertex AI
        prediction = await self.vertex_ai.predict(features)
        
        # Add confidence intervals if requested
        if include_confidence:
            prediction["confidence_intervals"] = self._calculate_confidence_intervals(
                prediction["predicted_prices"],
                prediction.get("model_confidence", 0.75)
            )
        
        return {
            "contract_code": contract_code,
            "current_price": features["current_price"],
            "predicted_prices": prediction["predicted_prices"],
            "model_confidence": prediction["model_confidence"],
            "confidence_intervals": prediction.get("confidence_intervals", {}),
            "factors": prediction["factors"],
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_confidence_intervals(
        self, 
        predictions: List[Dict[str, Any]], 
        confidence: float
    ) -> Dict[str, List[float]]:
        """
        Calculate confidence intervals for predictions
        """
        intervals = {"lower": [], "upper": []}
        
        for pred in predictions:
            price = pred.get("price", 500)
            # Simple confidence interval calculation
            margin = price * (1 - confidence) * 0.1
            intervals["lower"].append(price - margin)
            intervals["upper"].append(price + margin)
        
        return intervals
    
    async def get_forecast_accuracy(self) -> Dict[str, Any]:
        """
        Get historical forecast accuracy metrics
        """
        # In production, would calculate from stored forecasts vs actuals
        return {
            "mae": 2.5,  # Mean Absolute Error
            "rmse": 3.2,  # Root Mean Square Error
            "mape": 0.5,  # Mean Absolute Percentage Error
            "accuracy_rate": 0.82,  # 82% accuracy
            "sample_size": 100,
            "period": "last_30_days"
        }
    
    async def get_ensemble_forecast(
        self,
        contract_code: str,
        horizon_days: int = 7
    ) -> Dict[str, Any]:
        """
        Generate ensemble forecast using multiple models
        """
        # Get predictions from multiple sources
        vertex_forecast = await self.generate_forecast(contract_code, horizon_days)
        
        # Simple moving average model
        ma_forecast = self._moving_average_forecast(contract_code, horizon_days)
        
        # ARIMA-like trend forecast
        trend_forecast = self._trend_forecast(contract_code, horizon_days)
        
        # Combine forecasts
        ensemble_prices = []
        for i in range(horizon_days):
            vertex_price = vertex_forecast["predicted_prices"][i]["price"] if i < len(vertex_forecast["predicted_prices"]) else 510
            ma_price = ma_forecast[i] if i < len(ma_forecast) else 510
            trend_price = trend_forecast[i] if i < len(trend_forecast) else 510
            
            # Weighted average
            ensemble_price = (vertex_price * 0.5 + ma_price * 0.3 + trend_price * 0.2)
            ensemble_prices.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
                "price": ensemble_price,
                "components": {
                    "vertex_ai": vertex_price,
                    "moving_average": ma_price,
                    "trend": trend_price
                }
            })
        
        return {
            "contract_code": contract_code,
            "ensemble_forecast": ensemble_prices,
            "model_weights": {
                "vertex_ai": 0.5,
                "moving_average": 0.3,
                "trend": 0.2
            },
            "confidence": 0.85
        }
    
    def _moving_average_forecast(self, contract_code: str, horizon_days: int) -> List[float]:
        """
        Simple moving average forecast
        """
        historical = self.data_store.get_historical_prices(contract_code)
        
        if historical.empty or 'close' not in historical.columns:
            # Return default forecast
            base_price = 508
            return [base_price + i * 0.5 for i in range(horizon_days)]
        
        # Calculate MA
        ma_period = min(20, len(historical))
        ma = historical['close'].tail(ma_period).mean()
        
        # Simple projection
        return [ma + i * 0.3 for i in range(horizon_days)]
    
    def _trend_forecast(self, contract_code: str, horizon_days: int) -> List[float]:
        """
        Simple trend-based forecast
        """
        historical = self.data_store.get_historical_prices(contract_code)
        
        if historical.empty or 'close' not in historical.columns or len(historical) < 5:
            # Return default forecast
            base_price = 508
            return [base_price + i * 0.8 for i in range(horizon_days)]
        
        # Calculate trend
        prices = historical['close'].tail(10).values
        x = np.arange(len(prices))
        
        # Simple linear regression
        coeffs = np.polyfit(x, prices, 1)
        trend = coeffs[0]
        
        # Project forward
        last_price = prices[-1]
        return [last_price + trend * (i + 1) for i in range(horizon_days)]

# Singleton instance
forecast_service = ForecastService()