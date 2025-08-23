#!/usr/bin/env python3
"""
Example client for NQH2O Vertex AI prediction service
"""

import json
import requests
from google.cloud import aiplatform
from datetime import datetime

class NQH2OClient:
    """Client for NQH2O prediction service"""
    
    def __init__(self, project_id, region, endpoint_id):
        self.project_id = project_id
        self.region = region
        self.endpoint_id = endpoint_id
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=region)
        self.endpoint = aiplatform.Endpoint(endpoint_id)
    
    def predict(self, features):
        """Make prediction using Vertex AI endpoint"""
        try:
            # Prepare instances
            instances = [features] if isinstance(features, dict) else features
            
            # Make prediction
            response = self.endpoint.predict(instances=instances)
            
            return response.predictions[0]
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            raise
    
    def predict_with_example_data(self):
        """Make prediction with example data"""
        # Example features (replace with actual values)
        example_features = {
            'nqh2o_lag_1': 400.0,
            'nqh2o_lag_2': 395.0,
            'nqh2o_lag_4': 390.0,
            'time_trend': 1000.0,
            'drought_composite_spi': -1.5,
            'drought_composite_spei': -1.2,
            'drought_composite_pdsi': -2.0,
            'severe_drought_indicator': 1.0,
            'extreme_drought_indicator': 0.0,
            'drought_trend_4w': -0.5,
            'drought_trend_8w': -0.8,
            'price_momentum_4w': 0.02,
            'price_momentum_8w': 0.05,
            'price_volatility_4w': 15.0,
            'price_volatility_8w': 18.0,
            'price_vs_ma_4w': 0.01,
            'price_vs_ma_12w': 0.03,
            'month_sin': 0.5,
            'month_cos': 0.866,
            'week_sin': 0.0,
            'week_cos': 1.0,
            'is_drought_season': 1.0,
            'is_wet_season': 0.0
        }
        
        # Add remaining features with default values
        all_features = {feature: 0.0 for feature in range(29)}  # Adjust based on actual feature count
        all_features.update(example_features)
        
        result = self.predict(all_features)
        
        print("Prediction Result:")
        print(json.dumps(result, indent=2))
        
        return result

# Example usage
if __name__ == "__main__":
    # Configuration (replace with your values)
    PROJECT_ID = "your-project-id"
    REGION = "us-central1"
    ENDPOINT_ID = "your-endpoint-id"  # Get this from deployment
    
    # Create client
    client = NQH2OClient(PROJECT_ID, REGION, ENDPOINT_ID)
    
    # Make prediction
    result = client.predict_with_example_data()
