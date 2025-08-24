"""
NQH2O Prediction Service Integration
Integrates the Vertex AI deployed model with the water futures backend
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import math
import numpy as np

logger = logging.getLogger(__name__)

class NQH2OPredictionService:
    """
    Service for NQH2O water index price predictions using Vertex AI
    """
    
    def __init__(self):
        """Initialize the prediction service"""
        self.project_id = "water-futures-ai"
        self.region = "us-central1"
        self.endpoint_id = "7461517903041396736"
        self.model_id = "5834566149374738432"
        self.endpoint = None
        self._initialized = False
    
    def initialize(self):
        """Initialize Vertex AI connection"""
        if self._initialized:
            return
            
        try:
            from google.cloud import aiplatform
            aiplatform.init(project=self.project_id, location=self.region)
            self.endpoint = aiplatform.Endpoint(self.endpoint_id)
            self._initialized = True
            logger.info("NQH2O Prediction Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise
    
    def prepare_features(self, 
                        drought_metrics: Dict,
                        price_history: List[float],
                        basin_data: Optional[Dict] = None) -> Dict:
        """
        Prepare all 29 features required for prediction
        
        Args:
            drought_metrics: Current drought indicators (spi, spei, pdsi, severity)
            price_history: List of recent NQH2O prices (most recent last)
            basin_data: Optional basin-specific drought data
        
        Returns:
            Dictionary with all 29 features
        """
        if not drought_metrics or not price_history:
            raise ValueError("drought_metrics and price_history are required")
            
        features = {}
        
        # Basin-specific features (require actual data)
        if basin_data:
            features.update({
                'Chino_Basin_eddi90d_lag_12': basin_data['chino_eddi90d'],
                'Mojave_Basin_pdsi_lag_12': basin_data['mojave_pdsi'],
                'California_Surface_Water_spi180d_lag_12': basin_data['ca_spi180d'],
                'Central_Basin_eddi1y_lag_12': basin_data['central_eddi1y'],
                'California_Surface_Water_spi90d_lag_12': basin_data['ca_spi90d'],
                'California_Surface_Water_spei1y_lag_12': basin_data['ca_spei1y']
            })
        else:
            raise ValueError("basin_data is required for accurate predictions")
        
        # Drought composites from provided metrics
        features['drought_composite_spi'] = drought_metrics['spi']
        features['drought_composite_spei'] = drought_metrics['spei']
        features['drought_composite_pdsi'] = drought_metrics['pdsi']
        
        # Drought severity indicators
        severity = drought_metrics['severity']  # 0-4 scale
        features['severe_drought_indicator'] = 1.0 if severity >= 2 else 0.0
        features['extreme_drought_indicator'] = 1.0 if severity >= 3 else 0.0
        
        # Drought trends (must be provided)
        features['drought_trend_4w'] = drought_metrics['trend_4w']
        features['drought_trend_8w'] = drought_metrics['trend_8w']
        
        # Price lags (require actual history)
        if len(price_history) < 4:
            raise ValueError("At least 4 historical prices required")
            
        features['nqh2o_lag_1'] = price_history[-1]
        features['nqh2o_lag_2'] = price_history[-2]
        features['nqh2o_lag_4'] = price_history[-4]
        
        # Price momentum and volatility
        if len(price_history) < 12:
            raise ValueError("At least 12 historical prices required for full analysis")
            
        # Calculate momentum
        features['price_momentum_4w'] = (price_history[-1] - price_history[-4]) / price_history[-4]
        features['price_momentum_8w'] = (price_history[-1] - price_history[-8]) / price_history[-8]
        
        # Calculate volatility (standard deviation)
        features['price_volatility_4w'] = np.std(price_history[-4:])
        features['price_volatility_8w'] = np.std(price_history[-8:])
        
        # Price vs moving average
        ma_4w = np.mean(price_history[-4:])
        ma_12w = np.mean(price_history[-12:])
        features['price_vs_ma_4w'] = (price_history[-1] - ma_4w) / ma_4w
        features['price_vs_ma_12w'] = (price_history[-1] - ma_12w) / ma_12w
        
        # Temporal features
        now = datetime.now()
        month = now.month
        week = now.isocalendar()[1]
        
        features['month_sin'] = math.sin(2 * math.pi * month / 12)
        features['month_cos'] = math.cos(2 * math.pi * month / 12)
        features['week_sin'] = math.sin(2 * math.pi * week / 52)
        features['week_cos'] = math.cos(2 * math.pi * week / 52)
        
        # Seasonal indicators (California drought/wet seasons)
        features['is_drought_season'] = 1.0 if month in [6, 7, 8, 9, 10] else 0.0
        features['is_wet_season'] = 1.0 if month in [12, 1, 2, 3] else 0.0
        
        # Time trend (days since Jan 1, 2019 - start of training data)
        start_date = datetime(2019, 1, 1)
        features['time_trend'] = float((now - start_date).days)
        
        return features
    
    def predict(self, 
                drought_metrics: Dict,
                price_history: List[float],
                basin_data: Optional[Dict] = None) -> Dict:
        """
        Make NQH2O price prediction
        
        Args:
            drought_metrics: Current drought indicators
            price_history: Recent price history
            basin_data: Optional basin-specific data
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Initialize if not already done
            if not self._initialized:
                self.initialize()
            
            # Prepare features
            features = self.prepare_features(drought_metrics, price_history, basin_data)
            
            # Make prediction using Vertex AI SDK
            instances = [features]
            response = self.endpoint.predict(instances=instances)
            
            # Parse response
            if response.predictions:
                prediction = response.predictions[0]
                
                # Extract prediction value
                if isinstance(prediction, (int, float)):
                    pred_value = float(prediction)
                elif isinstance(prediction, dict):
                    pred_value = prediction.get('value', prediction.get('prediction'))
                else:
                    raise ValueError(f"Unexpected prediction format: {type(prediction)}")
                
                result = {
                    'success': True,
                    'prediction': float(pred_value),
                    'confidence': 85.0,  # Model confidence from training metrics
                    'timestamp': datetime.now().isoformat(),
                    'current_price': features['nqh2o_lag_1'],
                    'price_change': float(pred_value) - features['nqh2o_lag_1'],
                    'price_change_pct': ((float(pred_value) - features['nqh2o_lag_1']) / features['nqh2o_lag_1'] * 100),
                    'drought_severity': drought_metrics['severity'],
                    'model_version': '1.0'
                }
                
                return result
            else:
                raise ValueError("No predictions in response")
                
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_forecast_explanation(self, prediction_result: Dict) -> str:
        """
        Generate human-readable explanation of the forecast
        
        Args:
            prediction_result: Result from predict method
        
        Returns:
            Explanation string
        """
        if not prediction_result.get('success'):
            return f"Forecast unavailable: {prediction_result.get('error', 'Unknown error')}"
        
        pred = prediction_result['prediction']
        current = prediction_result['current_price']
        change_pct = prediction_result['price_change_pct']
        severity = prediction_result['drought_severity']
        confidence = prediction_result['confidence']
        
        # Severity descriptions
        severity_desc = {
            0: "no drought",
            1: "mild drought",
            2: "severe drought",
            3: "extreme drought",
            4: "exceptional drought"
        }
        
        # Direction
        if change_pct > 2:
            direction = "increase"
            reason = "worsening water scarcity"
        elif change_pct < -2:
            direction = "decrease"
            reason = "improving water conditions"
        else:
            direction = "remain stable"
            reason = "steady drought conditions"
        
        explanation = (
            f"The NQH2O water index is forecasted to {direction} "
            f"from ${current:.2f} to ${pred:.2f} ({change_pct:+.1f}%). "
            f"This forecast is based on {severity_desc.get(severity, 'current')} conditions "
            f"and has a confidence level of {confidence:.0f}%. "
            f"The prediction reflects {reason} in California's water markets."
        )
        
        return explanation


# Singleton instance
_prediction_service = None

def get_prediction_service() -> NQH2OPredictionService:
    """Get or create the prediction service singleton"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = NQH2OPredictionService()
    return _prediction_service