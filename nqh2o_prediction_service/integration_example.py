#!/usr/bin/env python3
"""
Integration example for NQH2O Vertex AI prediction service
This shows how to integrate the deployed model with your existing Python backend
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from google.cloud import aiplatform
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class NQH2OPredictionService:
    """
    Service class for integrating NQH2O predictions into your backend
    """
    
    def __init__(self, 
                 project_id: str = "water-futures-ai",
                 region: str = "us-central1",
                 model_id: str = "5834566149374738432",
                 endpoint_id: Optional[str] = None):
        """
        Initialize the prediction service
        
        Args:
            project_id: GCP project ID
            region: Deployment region
            model_id: Vertex AI model ID
            endpoint_id: Vertex AI endpoint ID (optional)
        """
        self.project_id = project_id
        self.region = region
        self.model_id = model_id
        self.endpoint_id = endpoint_id
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=region)
        
        # Get or create endpoint
        if endpoint_id:
            self.endpoint = aiplatform.Endpoint(endpoint_id)
        else:
            # Deploy model to a new endpoint
            self.endpoint = self._deploy_model()
    
    def _deploy_model(self):
        """Deploy model to a new endpoint"""
        try:
            logger.info("Deploying model to new endpoint...")
            
            # Get model
            model = aiplatform.Model(self.model_id)
            
            # Create and deploy to endpoint
            endpoint = model.deploy(
                deployed_model_display_name="nqh2o-deployment",
                machine_type="n1-standard-2",
                min_replica_count=1,
                max_replica_count=3,
                accelerator_type=None,
                accelerator_count=0,
                sync=True
            )
            
            logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")
            return endpoint
            
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            raise
    
    def prepare_features(self, 
                        drought_data: Dict,
                        price_history: List[float],
                        temporal_info: Dict) -> Dict:
        """
        Prepare features for prediction
        
        Args:
            drought_data: Dictionary with drought indicators
            price_history: List of recent NQH2O prices
            temporal_info: Dictionary with temporal features
        
        Returns:
            Dictionary of features ready for prediction
        """
        features = {}
        
        # Price lags
        if len(price_history) >= 1:
            features['nqh2o_lag_1'] = price_history[-1]
        if len(price_history) >= 2:
            features['nqh2o_lag_2'] = price_history[-2]
        if len(price_history) >= 4:
            features['nqh2o_lag_4'] = price_history[-4]
        
        # Drought composites
        features['drought_composite_spi'] = drought_data.get('spi', 0.0)
        features['drought_composite_spei'] = drought_data.get('spei', 0.0)
        features['drought_composite_pdsi'] = drought_data.get('pdsi', 0.0)
        
        # Drought indicators
        features['severe_drought_indicator'] = 1.0 if drought_data.get('severity', 0) >= 2 else 0.0
        features['extreme_drought_indicator'] = 1.0 if drought_data.get('severity', 0) >= 3 else 0.0
        
        # Drought trends
        features['drought_trend_4w'] = drought_data.get('trend_4w', 0.0)
        features['drought_trend_8w'] = drought_data.get('trend_8w', 0.0)
        
        # Price momentum and volatility
        if len(price_history) >= 8:
            features['price_momentum_4w'] = (price_history[-1] - price_history[-4]) / price_history[-4] if price_history[-4] != 0 else 0
            features['price_momentum_8w'] = (price_history[-1] - price_history[-8]) / price_history[-8] if price_history[-8] != 0 else 0
            
            # Simple volatility calculation
            import numpy as np
            features['price_volatility_4w'] = np.std(price_history[-4:]) if len(price_history[-4:]) > 1 else 0
            features['price_volatility_8w'] = np.std(price_history[-8:]) if len(price_history[-8:]) > 1 else 0
            
            # Price vs moving average
            ma_4w = np.mean(price_history[-4:])
            ma_12w = np.mean(price_history[-12:]) if len(price_history) >= 12 else ma_4w
            features['price_vs_ma_4w'] = (price_history[-1] - ma_4w) / ma_4w if ma_4w != 0 else 0
            features['price_vs_ma_12w'] = (price_history[-1] - ma_12w) / ma_12w if ma_12w != 0 else 0
        else:
            # Default values if not enough history
            for key in ['price_momentum_4w', 'price_momentum_8w', 'price_volatility_4w', 
                       'price_volatility_8w', 'price_vs_ma_4w', 'price_vs_ma_12w']:
                features[key] = 0.0
        
        # Temporal features
        features.update(temporal_info)
        
        # Basin-specific features (set to 0 if not available)
        basin_features = [
            'Chino_Basin_eddi90d_lag_12',
            'Mojave_Basin_pdsi_lag_12',
            'California_Surface_Water_spi180d_lag_12',
            'Central_Basin_eddi1y_lag_12',
            'California_Surface_Water_spi90d_lag_12',
            'California_Surface_Water_spei1y_lag_12'
        ]
        
        for feature in basin_features:
            features[feature] = drought_data.get(feature, 0.0)
        
        return features
    
    def predict(self, features: Dict) -> Dict:
        """
        Make prediction using Vertex AI endpoint
        
        Args:
            features: Dictionary of input features
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Prepare instance for prediction
            instances = [features]
            
            # Make prediction
            response = self.endpoint.predict(instances=instances)
            
            # Parse response
            result = {
                'prediction': response.predictions[0] if response.predictions else None,
                'model_id': self.model_id,
                'timestamp': datetime.now().isoformat(),
                'features_used': list(features.keys())
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def predict_with_confidence(self, features: Dict, n_samples: int = 10) -> Dict:
        """
        Make prediction with confidence intervals using multiple predictions
        
        Args:
            features: Dictionary of input features
            n_samples: Number of predictions to make for confidence estimation
        
        Returns:
            Dictionary with prediction and confidence intervals
        """
        try:
            predictions = []
            
            # Make multiple predictions (in production, you might add noise to features)
            for _ in range(n_samples):
                result = self.predict(features)
                if 'prediction' in result and result['prediction']:
                    predictions.append(result['prediction'])
            
            if predictions:
                import numpy as np
                pred_array = np.array(predictions)
                
                return {
                    'prediction': float(np.mean(pred_array)),
                    'confidence_interval': {
                        'lower': float(np.percentile(pred_array, 5)),
                        'upper': float(np.percentile(pred_array, 95))
                    },
                    'std_deviation': float(np.std(pred_array)),
                    'n_samples': len(predictions),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': 'No valid predictions', 'timestamp': datetime.now().isoformat()}
                
        except Exception as e:
            logger.error(f"Confidence prediction error: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}


# Example usage with your existing backend
def integrate_with_backend():
    """
    Example of how to integrate with your existing water futures backend
    """
    # Initialize the service
    service = NQH2OPredictionService(
        project_id="water-futures-ai",
        region="us-central1",
        model_id="5834566149374738432"
        # endpoint_id will be set after first deployment
    )
    
    # Example data from your backend
    drought_data = {
        'spi': -1.5,        # Standardized Precipitation Index
        'spei': -1.2,       # Standardized Precipitation-Evapotranspiration Index
        'pdsi': -2.0,       # Palmer Drought Severity Index
        'severity': 2,      # Drought severity level (0-4)
        'trend_4w': -0.5,   # 4-week drought trend
        'trend_8w': -0.8,   # 8-week drought trend
    }
    
    # Historical NQH2O prices (most recent last)
    price_history = [380, 385, 390, 388, 392, 395, 398, 400, 402, 405, 403, 400]
    
    # Temporal features
    import math
    month = datetime.now().month
    week = datetime.now().isocalendar()[1]
    
    temporal_info = {
        'time_trend': 1000.0,  # Days since start of data
        'month_sin': math.sin(2 * math.pi * month / 12),
        'month_cos': math.cos(2 * math.pi * month / 12),
        'week_sin': math.sin(2 * math.pi * week / 52),
        'week_cos': math.cos(2 * math.pi * week / 52),
        'is_drought_season': 1.0 if month in [6, 7, 8, 9, 10] else 0.0,
        'is_wet_season': 1.0 if month in [12, 1, 2, 3] else 0.0
    }
    
    # Prepare features
    features = service.prepare_features(drought_data, price_history, temporal_info)
    
    # Make prediction
    result = service.predict(features)
    
    print("Prediction Result:")
    print(json.dumps(result, indent=2))
    
    # Make prediction with confidence intervals
    confidence_result = service.predict_with_confidence(features, n_samples=5)
    
    print("\nPrediction with Confidence:")
    print(json.dumps(confidence_result, indent=2))
    
    return result


# FastAPI integration example
def create_prediction_endpoint(app):
    """
    Example of adding prediction endpoint to FastAPI app
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    
    class PredictionRequest(BaseModel):
        drought_data: Dict
        price_history: List[float]
        temporal_info: Dict
    
    class PredictionResponse(BaseModel):
        prediction: float
        confidence_interval: Optional[Dict]
        timestamp: str
        error: Optional[str]
    
    # Initialize service
    prediction_service = NQH2OPredictionService()
    
    @app.post("/api/nqh2o/predict", response_model=PredictionResponse)
    async def predict_nqh2o(request: PredictionRequest):
        """
        Predict NQH2O water index price
        """
        try:
            # Prepare features
            features = prediction_service.prepare_features(
                request.drought_data,
                request.price_history,
                request.temporal_info
            )
            
            # Make prediction with confidence
            result = prediction_service.predict_with_confidence(features)
            
            if 'error' in result:
                raise HTTPException(status_code=500, detail=result['error'])
            
            return PredictionResponse(**result)
            
        except Exception as e:
            logger.error(f"Prediction endpoint error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run integration example
    integrate_with_backend()