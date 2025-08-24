#!/usr/bin/env python3
"""
Test script for deployed NQH2O model on Vertex AI
"""

import json
import sys
from datetime import datetime
import math

# Try to import google-cloud-aiplatform, install if not available
try:
    from google.cloud import aiplatform
except ImportError:
    print("Installing google-cloud-aiplatform...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-aiplatform"])
    from google.cloud import aiplatform

def test_vertex_deployment():
    """Test the deployed model with sample data"""
    
    # Configuration
    PROJECT_ID = "water-futures-ai"
    REGION = "us-central1"
    ENDPOINT_ID = "7461517903041396736"
    
    print(f"Testing NQH2O Model Deployment")
    print(f"Project: {PROJECT_ID}")
    print(f"Region: {REGION}")
    print(f"Endpoint ID: {ENDPOINT_ID}")
    print("-" * 50)
    
    # Initialize Vertex AI
    aiplatform.init(project=PROJECT_ID, location=REGION)
    
    # Get endpoint
    endpoint = aiplatform.Endpoint(ENDPOINT_ID)
    
    # Prepare test features (all 29 features required)
    month = datetime.now().month
    week = datetime.now().isocalendar()[1]
    
    test_features = {
        # Basin-specific drought features
        'Chino_Basin_eddi90d_lag_12': -0.5,
        'Mojave_Basin_pdsi_lag_12': -1.2,
        'California_Surface_Water_spi180d_lag_12': -0.8,
        'Central_Basin_eddi1y_lag_12': -0.6,
        'California_Surface_Water_spi90d_lag_12': -0.7,
        'California_Surface_Water_spei1y_lag_12': -0.9,
        
        # Drought composites
        'drought_composite_spi': -1.5,
        'drought_composite_spei': -1.2,
        'drought_composite_pdsi': -2.0,
        
        # Drought indicators
        'severe_drought_indicator': 1.0,
        'extreme_drought_indicator': 0.0,
        
        # Drought trends
        'drought_trend_4w': -0.5,
        'drought_trend_8w': -0.8,
        
        # Price lags (recent NQH2O prices)
        'nqh2o_lag_1': 400.0,
        'nqh2o_lag_2': 395.0,
        'nqh2o_lag_4': 390.0,
        
        # Price momentum and volatility
        'price_momentum_4w': 0.026,  # (400-390)/390
        'price_momentum_8w': 0.053,  # Assuming 380 8 weeks ago
        'price_volatility_4w': 15.0,
        'price_volatility_8w': 18.0,
        'price_vs_ma_4w': 0.01,
        'price_vs_ma_12w': 0.03,
        
        # Temporal features
        'month_sin': math.sin(2 * math.pi * month / 12),
        'month_cos': math.cos(2 * math.pi * month / 12),
        'week_sin': math.sin(2 * math.pi * week / 52),
        'week_cos': math.cos(2 * math.pi * week / 52),
        'is_drought_season': 1.0 if month in [6, 7, 8, 9, 10] else 0.0,
        'is_wet_season': 1.0 if month in [12, 1, 2, 3] else 0.0,
        'time_trend': 1000.0  # Days since start of training data
    }
    
    print("\nTest Features:")
    print(f"  Current NQH2O Price (lag_1): ${test_features['nqh2o_lag_1']}")
    print(f"  Drought Composite SPI: {test_features['drought_composite_spi']}")
    print(f"  Severe Drought: {'Yes' if test_features['severe_drought_indicator'] else 'No'}")
    print(f"  Drought Season: {'Yes' if test_features['is_drought_season'] else 'No'}")
    print()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Current Conditions",
            "features": test_features
        },
        {
            "name": "Worsening Drought",
            "features": {**test_features, 
                        'drought_composite_spi': -2.5,
                        'drought_composite_spei': -2.2,
                        'drought_composite_pdsi': -3.0,
                        'extreme_drought_indicator': 1.0}
        },
        {
            "name": "Improving Conditions",
            "features": {**test_features,
                        'drought_composite_spi': -0.5,
                        'drought_composite_spei': -0.3,
                        'drought_composite_pdsi': -0.8,
                        'severe_drought_indicator': 0.0}
        },
        {
            "name": "High Price Volatility",
            "features": {**test_features,
                        'price_volatility_4w': 30.0,
                        'price_volatility_8w': 35.0,
                        'price_momentum_4w': 0.08}
        }
    ]
    
    print("Running predictions for different scenarios...")
    print("=" * 50)
    
    for scenario in scenarios:
        try:
            print(f"\nScenario: {scenario['name']}")
            print("-" * 30)
            
            # Make prediction
            instances = [scenario['features']]
            response = endpoint.predict(instances=instances)
            
            # Parse response
            if hasattr(response, 'predictions') and response.predictions:
                prediction = response.predictions[0]
                
                # Handle different response formats
                if isinstance(prediction, dict):
                    if 'predictions' in prediction:
                        pred_value = prediction['predictions'][0] if isinstance(prediction['predictions'], list) else prediction['predictions']
                    else:
                        pred_value = prediction.get('prediction', prediction)
                    
                    print(f"  Predicted NQH2O Price: ${pred_value:.2f}")
                    
                    # Show individual model predictions if available
                    if 'individual_predictions' in prediction:
                        print("  Individual Model Predictions:")
                        for model, pred in prediction['individual_predictions'].items():
                            model_pred = pred[0] if isinstance(pred, list) else pred
                            print(f"    - {model}: ${model_pred:.2f}")
                else:
                    print(f"  Predicted NQH2O Price: ${prediction:.2f}")
                
                # Calculate change from current price
                current_price = scenario['features']['nqh2o_lag_1']
                if isinstance(prediction, dict):
                    pred_value = prediction.get('predictions', [prediction])[0] if 'predictions' in prediction else prediction
                else:
                    pred_value = prediction
                    
                if isinstance(pred_value, (int, float)):
                    change = pred_value - current_price
                    change_pct = (change / current_price) * 100
                    print(f"  Change from Current: ${change:.2f} ({change_pct:+.1f}%)")
            else:
                print(f"  Error: No predictions in response")
                
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("\nIntegration Instructions:")
    print("1. Use the integration_example.py for backend integration")
    print("2. The model expects all 29 features as shown above")
    print("3. Predictions return NQH2O price in USD")
    print("4. Model performs best with recent price history and drought data")
    
    return True

if __name__ == "__main__":
    try:
        test_vertex_deployment()
    except Exception as e:
        print(f"Test failed: {str(e)}")
        sys.exit(1)