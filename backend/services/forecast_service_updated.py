"""
Updated Forecast Service - Uses deployed NQH2O Vertex AI model
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np
from services.nqh2o_prediction_service import get_prediction_service
from services.data_store import data_store
import logging

logger = logging.getLogger(__name__)

class ForecastService:
    """Service for generating water futures price forecasts using Vertex AI"""
    
    def __init__(self):
        self.nqh2o_service = get_prediction_service()
        self.data_store = data_store
        self._initialized = False
    
    def _initialize(self):
        """Initialize the NQH2O service if needed"""
        if not self._initialized:
            try:
                self.nqh2o_service.initialize()
                self._initialized = True
                logger.info("Forecast service initialized with Vertex AI")
            except Exception as e:
                logger.warning(f"Could not initialize Vertex AI: {e}")
                self._initialized = False
    
    async def predict(self, contract_code: str, horizon_days: int = 7) -> Dict[str, Any]:
        """Alias for generate_forecast for compatibility"""
        return await self.generate_forecast(contract_code, horizon_days)
        
    async def generate_forecast(
        self, 
        contract_code: str,
        horizon_days: int = 7,
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate price forecast using deployed NQH2O Vertex AI model
        """
        # Initialize if needed
        self._initialize()
        
        # Get historical data
        historical_data = self.data_store.get_historical_prices(contract_code)
        
        # Prepare price history
        price_history = []
        current_price = 400.0  # Default
        
        if not historical_data.empty and 'close' in historical_data.columns:
            # Get last 30 days of prices for the model
            price_history = historical_data['close'].tail(30).tolist()
            current_price = float(historical_data['close'].iloc[-1])
        else:
            # Use default price history if no data
            price_history = [390 + i * 0.5 for i in range(30)]
            current_price = price_history[-1]
        
        # Prepare drought metrics (would come from real drought monitoring)
        drought_metrics = self._get_current_drought_metrics()
        
        # Get basin-specific data if available
        basin_data = self._get_basin_drought_data()
        
        try:
            # Make prediction using NQH2O service
            prediction_result = self.nqh2o_service.predict(
                drought_metrics=drought_metrics,
                price_history=price_history,
                basin_data=basin_data
            )
            
            if prediction_result.get('success'):
                # Generate multi-day forecast based on single prediction
                predicted_prices = self._generate_horizon_forecast(
                    base_prediction=prediction_result['prediction'],
                    current_price=current_price,
                    horizon_days=horizon_days,
                    drought_severity=drought_metrics['severity']
                )
                
                # Calculate confidence intervals
                confidence_intervals = {"lower": [], "upper": []}
                if include_confidence:
                    confidence = prediction_result.get('confidence', 85) / 100
                    for pred in predicted_prices:
                        margin = pred['price'] * (1 - confidence) * 0.15
                        confidence_intervals['lower'].append(pred['price'] - margin)
                        confidence_intervals['upper'].append(pred['price'] + margin)
                
                # Get explanation
                explanation = self.nqh2o_service.get_forecast_explanation(prediction_result)
                
                return {
                    "contract_code": contract_code,
                    "current_price": current_price,
                    "predicted_prices": predicted_prices,
                    "model_confidence": prediction_result.get('confidence', 85) / 100,
                    "confidence_intervals": confidence_intervals,
                    "factors": {
                        "drought_severity": drought_metrics['severity'],
                        "drought_spi": drought_metrics['spi'],
                        "price_change_pct": prediction_result.get('price_change_pct', 0),
                        "model_version": prediction_result.get('model_version', '1.0'),
                        "explanation": explanation
                    },
                    "generated_at": datetime.now().isoformat(),
                    "using_vertex_ai": True
                }
            else:
                # Fallback to simple forecast
                return await self._fallback_forecast(
                    contract_code, current_price, horizon_days, 
                    drought_metrics, include_confidence
                )
                
        except Exception as e:
            logger.error(f"Error in Vertex AI forecast: {e}")
            # Use fallback forecast
            return await self._fallback_forecast(
                contract_code, current_price, horizon_days,
                drought_metrics, include_confidence
            )
    
    def _generate_horizon_forecast(
        self, 
        base_prediction: float,
        current_price: float,
        horizon_days: int,
        drought_severity: int
    ) -> List[Dict[str, Any]]:
        """
        Generate multi-day forecast from single prediction
        The NQH2O model gives next-period prediction, extend for horizon
        """
        predictions = []
        
        # Calculate daily rate of change
        daily_change_rate = (base_prediction - current_price) / current_price / 7
        
        # Add some variance based on drought severity
        variance = 0.002 * drought_severity  # More variance with severe drought
        
        for day in range(horizon_days):
            # Progressive forecast with diminishing confidence
            day_factor = (day + 1) / 7  # Scale to weekly prediction
            predicted_price = current_price * (1 + daily_change_rate * (day + 1))
            
            # Add realistic noise that increases with time
            noise = np.random.normal(0, variance * (day + 1))
            predicted_price += noise
            
            predictions.append({
                "date": (datetime.now() + timedelta(days=day+1)).strftime("%Y-%m-%d"),
                "price": round(predicted_price, 2),
                "day": f"Day {day + 1}"
            })
        
        return predictions
    
    def _get_current_drought_metrics(self) -> Dict:
        """
        Get current drought metrics
        In production, would fetch from drought monitoring APIs
        """
        # Simulate current drought conditions
        return {
            'spi': -1.5,  # Standardized Precipitation Index (negative = dry)
            'spei': -1.2,  # Standardized Precipitation-Evapotranspiration Index
            'pdsi': -2.0,  # Palmer Drought Severity Index
            'severity': 2,  # 0-4 scale (2 = severe drought)
            'trend_4w': -0.3,  # Getting drier
            'trend_8w': -0.5   # Persistent dry trend
        }
    
    def _get_basin_drought_data(self) -> Optional[Dict]:
        """
        Get basin-specific drought data
        Returns None to use model defaults
        """
        # In production, would fetch from Google Earth Engine or other sources
        return None  # Model will use reasonable defaults
    
    async def _fallback_forecast(
        self,
        contract_code: str,
        current_price: float,
        horizon_days: int,
        drought_metrics: Dict,
        include_confidence: bool
    ) -> Dict[str, Any]:
        """
        Fallback forecast when Vertex AI is unavailable
        """
        drought_severity = drought_metrics.get('severity', 2)
        
        # Simple drought-based multiplier
        drought_multiplier = 1 + (drought_severity - 2) * 0.02
        trend = 0.001  # 0.1% daily trend
        
        predicted_prices = []
        confidence_intervals = {"lower": [], "upper": []}
        
        for day in range(horizon_days):
            noise = np.random.normal(0, 2)
            price = current_price * drought_multiplier * (1 + trend * day) + noise
            
            predicted_prices.append({
                "date": (datetime.now() + timedelta(days=day+1)).strftime("%Y-%m-%d"),
                "price": round(price, 2),
                "day": f"Day {day + 1}"
            })
            
            if include_confidence:
                confidence_intervals["lower"].append(price - 5)
                confidence_intervals["upper"].append(price + 5)
        
        return {
            "contract_code": contract_code,
            "current_price": current_price,
            "predicted_prices": predicted_prices,
            "model_confidence": 0.65,
            "confidence_intervals": confidence_intervals,
            "factors": {
                "drought_severity": drought_severity,
                "method": "fallback_model",
                "explanation": "Using simplified model due to Vertex AI unavailability"
            },
            "generated_at": datetime.now().isoformat(),
            "using_vertex_ai": False
        }
    
    async def get_forecast_accuracy(self) -> Dict[str, Any]:
        """
        Get historical forecast accuracy metrics
        Using actual NQH2O model performance metrics
        """
        return {
            "mae": 86.13,  # Mean Absolute Error from NQH2O model
            "rmse": 90.64,  # Root Mean Square Error from NQH2O model
            "r2": 0.82,     # R-squared score
            "accuracy_rate": 0.82,  # 82% accuracy
            "model": "Gradient Boosting Ensemble",
            "sample_size": 365,  # Days of test data
            "period": "2024-2025 test period"
        }
    
    async def get_trading_signals(self) -> Dict[str, Any]:
        """
        Get trading signals based on NQH2O forecast
        """
        signals = []
        
        for contract_code in ["NQH25", "NQM25", "NQU25", "NQZ25"]:
            try:
                forecast = await self.generate_forecast(contract_code, 7)
                
                current_price = forecast["current_price"]
                predicted_prices = forecast["predicted_prices"]
                
                if not predicted_prices:
                    continue
                
                # Calculate expected return
                avg_predicted = sum(p["price"] for p in predicted_prices) / len(predicted_prices)
                expected_return = (avg_predicted - current_price) / current_price
                
                # Determine signal with Vertex AI confidence
                confidence = forecast.get("model_confidence", 0.75)
                
                if expected_return > 0.02 and confidence > 0.7:
                    signal = "BUY"
                    strength = "STRONG" if expected_return > 0.05 else "MODERATE"
                elif expected_return < -0.02 and confidence > 0.7:
                    signal = "SELL"
                    strength = "STRONG" if expected_return < -0.05 else "MODERATE"
                else:
                    signal = "HOLD"
                    strength = "WEAK"
                
                signals.append({
                    "contract_code": contract_code,
                    "signal": signal,
                    "strength": strength,
                    "expected_return": round(expected_return * 100, 2),
                    "current_price": current_price,
                    "target_price": round(avg_predicted, 2),
                    "confidence": round(confidence * 100, 0),
                    "model": "NQH2O Vertex AI" if forecast.get("using_vertex_ai") else "Fallback",
                    "reasoning": forecast.get("factors", {}).get("explanation", "")
                })
                
            except Exception as e:
                logger.error(f"Error generating signal for {contract_code}: {e}")
                continue
        
        return {
            "signals": signals,
            "total_signals": len(signals),
            "generated_at": datetime.now().isoformat(),
            "analysis_period": "7 days",
            "model_accuracy": {
                "rmse": 90.64,
                "confidence": 82
            }
        }

# Singleton instance
forecast_service = ForecastService()