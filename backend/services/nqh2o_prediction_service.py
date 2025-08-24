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
        features = {}
        
        # Basin-specific features (use provided or default to moderate drought)
        if basin_data:
            features.update({
                'Chino_Basin_eddi90d_lag_12': basin_data.get('chino_eddi90d', -0.5),
                'Mojave_Basin_pdsi_lag_12': basin_data.get('mojave_pdsi', -1.0),
                'California_Surface_Water_spi180d_lag_12': basin_data.get('ca_spi180d', -0.8),
                'Central_Basin_eddi1y_lag_12': basin_data.get('central_eddi1y', -0.6),
                'California_Surface_Water_spi90d_lag_12': basin_data.get('ca_spi90d', -0.7),
                'California_Surface_Water_spei1y_lag_12': basin_data.get('ca_spei1y', -0.9)
            })
        else:
            # Default values based on typical drought conditions
            features.update({
                'Chino_Basin_eddi90d_lag_12': -0.5,
                'Mojave_Basin_pdsi_lag_12': -1.0,
                'California_Surface_Water_spi180d_lag_12': -0.8,
                'Central_Basin_eddi1y_lag_12': -0.6,
                'California_Surface_Water_spi90d_lag_12': -0.7,
                'California_Surface_Water_spei1y_lag_12': -0.9
            })
        
        # Drought composites from provided metrics
        features['drought_composite_spi'] = drought_metrics.get('spi', -1.0)
        features['drought_composite_spei'] = drought_metrics.get('spei', -0.8)
        features['drought_composite_pdsi'] = drought_metrics.get('pdsi', -1.5)
        
        # Drought severity indicators
        severity = drought_metrics.get('severity', 1)  # 0-4 scale
        features['severe_drought_indicator'] = 1.0 if severity >= 2 else 0.0
        features['extreme_drought_indicator'] = 1.0 if severity >= 3 else 0.0
        
        # Drought trends (calculate from history if available)
        features['drought_trend_4w'] = drought_metrics.get('trend_4w', -0.3)
        features['drought_trend_8w'] = drought_metrics.get('trend_8w', -0.5)
        
        # Price lags
        if price_history and len(price_history) > 0:
            features['nqh2o_lag_1'] = price_history[-1]
            features['nqh2o_lag_2'] = price_history[-2] if len(price_history) > 1 else price_history[-1]
            features['nqh2o_lag_4'] = price_history[-4] if len(price_history) > 3 else price_history[-1]
        else:
            # Default to average NQH2O price if no history
            features['nqh2o_lag_1'] = 400.0
            features['nqh2o_lag_2'] = 395.0
            features['nqh2o_lag_4'] = 390.0
        
        # Price momentum and volatility
        if price_history and len(price_history) >= 8:
            # Calculate momentum
            features['price_momentum_4w'] = (price_history[-1] - price_history[-4]) / price_history[-4] if price_history[-4] != 0 else 0
            features['price_momentum_8w'] = (price_history[-1] - price_history[-8]) / price_history[-8] if price_history[-8] != 0 else 0
            
            # Calculate volatility (standard deviation)
            features['price_volatility_4w'] = np.std(price_history[-4:]) if len(price_history[-4:]) > 1 else 10.0
            features['price_volatility_8w'] = np.std(price_history[-8:]) if len(price_history[-8:]) > 1 else 15.0
            
            # Price vs moving average
            ma_4w = np.mean(price_history[-4:])
            ma_12w = np.mean(price_history[-12:]) if len(price_history) >= 12 else ma_4w
            features['price_vs_ma_4w'] = (price_history[-1] - ma_4w) / ma_4w if ma_4w != 0 else 0
            features['price_vs_ma_12w'] = (price_history[-1] - ma_12w) / ma_12w if ma_12w != 0 else 0
        else:
            # Default values
            features['price_momentum_4w'] = 0.02
            features['price_momentum_8w'] = 0.05
            features['price_volatility_4w'] = 15.0
            features['price_volatility_8w'] = 18.0
            features['price_vs_ma_4w'] = 0.01
            features['price_vs_ma_12w'] = 0.03
        
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
            # Initialize if needed
            if not self._initialized:
                self.initialize()
            
            # Prepare features
            features = self.prepare_features(drought_metrics, price_history, basin_data)
            
            # Make prediction
            instances = [features]
            response = self.endpoint.predict(instances=instances)
            
            # Parse response
            if hasattr(response, 'predictions') and response.predictions:
                prediction = response.predictions[0]
                
                # Handle different response formats
                if isinstance(prediction, dict):
                    pred_value = prediction.get('predictions', [prediction])[0] if 'predictions' in prediction else prediction
                    individual_preds = prediction.get('individual_predictions', {})
                else:
                    pred_value = prediction
                    individual_preds = {}
                
                # Calculate confidence based on model agreement
                if individual_preds:
                    preds = [p[0] if isinstance(p, list) else p for p in individual_preds.values()]
                    std_dev = np.std(preds) if len(preds) > 1 else 5.0
                    confidence = max(0, min(100, 100 - (std_dev / pred_value * 100))) if pred_value != 0 else 50
                else:
                    confidence = 85  # Default confidence
                
                result = {
                    'success': True,
                    'prediction': float(pred_value),
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat(),
                    'current_price': features['nqh2o_lag_1'],
                    'price_change': float(pred_value) - features['nqh2o_lag_1'],
                    'price_change_pct': ((float(pred_value) - features['nqh2o_lag_1']) / features['nqh2o_lag_1'] * 100) if features['nqh2o_lag_1'] != 0 else 0,
                    'drought_severity': drought_metrics.get('severity', 1),
                    'model_version': '1.0',
                    'individual_predictions': individual_preds
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
            return "Forecast unavailable due to technical issues."
        
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