#!/usr/bin/env python3
"""
Direct test of deployed NQH2O model using gcloud credentials
"""

import json
import subprocess
import math
from datetime import datetime

def test_prediction():
    """Test the model with a direct prediction request"""
    
    # Prepare test features
    month = datetime.now().month
    week = datetime.now().isocalendar()[1]
    
    features = {
        'Chino_Basin_eddi90d_lag_12': -0.5,
        'Mojave_Basin_pdsi_lag_12': -1.2,
        'California_Surface_Water_spi180d_lag_12': -0.8,
        'Central_Basin_eddi1y_lag_12': -0.6,
        'California_Surface_Water_spi90d_lag_12': -0.7,
        'California_Surface_Water_spei1y_lag_12': -0.9,
        'drought_composite_spi': -1.5,
        'drought_composite_spei': -1.2,
        'drought_composite_pdsi': -2.0,
        'severe_drought_indicator': 1.0,
        'extreme_drought_indicator': 0.0,
        'drought_trend_4w': -0.5,
        'drought_trend_8w': -0.8,
        'nqh2o_lag_1': 400.0,
        'nqh2o_lag_2': 395.0,
        'nqh2o_lag_4': 390.0,
        'price_momentum_4w': 0.026,
        'price_momentum_8w': 0.053,
        'price_volatility_4w': 15.0,
        'price_volatility_8w': 18.0,
        'price_vs_ma_4w': 0.01,
        'price_vs_ma_12w': 0.03,
        'month_sin': math.sin(2 * math.pi * month / 12),
        'month_cos': math.cos(2 * math.pi * month / 12),
        'week_sin': math.sin(2 * math.pi * week / 52),
        'week_cos': math.cos(2 * math.pi * week / 52),
        'is_drought_season': 1.0 if month in [6, 7, 8, 9, 10] else 0.0,
        'is_wet_season': 1.0 if month in [12, 1, 2, 3] else 0.0,
        'time_trend': 1000.0
    }
    
    # Create request
    request = {
        "instances": [features]
    }
    
    # Save request to file
    with open('/tmp/test_request.json', 'w') as f:
        json.dump(request, f)
    
    print("Testing NQH2O Model Prediction")
    print("=" * 50)
    print(f"Current Price (lag_1): ${features['nqh2o_lag_1']}")
    print(f"Drought SPI: {features['drought_composite_spi']}")
    print(f"Severe Drought: {'Yes' if features['severe_drought_indicator'] else 'No'}")
    print()
    
    # Use gcloud to make prediction
    try:
        result = subprocess.run([
            'gcloud', 'ai', 'endpoints', 'predict',
            '7461517903041396736',
            '--region=us-central1',
            '--json-request=/tmp/test_request.json'
        ], capture_output=True, text=True, check=True)
        
        # Parse response
        if result.stdout:
            # Extract JSON from output (gcloud may add extra text)
            lines = result.stdout.split('\n')
            json_str = None
            for i, line in enumerate(lines):
                if line.strip().startswith('[') or line.strip().startswith('{'):
                    # Found start of JSON, collect until end
                    json_lines = []
                    for j in range(i, len(lines)):
                        json_lines.append(lines[j])
                        if lines[j].strip().endswith(']') or lines[j].strip().endswith('}'):
                            break
                    json_str = '\n'.join(json_lines)
                    break
            
            if json_str:
                response = json.loads(json_str)
                print("✅ Prediction Successful!")
                print(f"Response: {json.dumps(response, indent=2)}")
                
                # Extract prediction value
                if isinstance(response, list) and len(response) > 0:
                    pred = response[0]
                    if isinstance(pred, dict):
                        if 'predictions' in pred:
                            value = pred['predictions'][0] if isinstance(pred['predictions'], list) else pred['predictions']
                        else:
                            value = pred.get('prediction', pred)
                    else:
                        value = pred
                    
                    print(f"\n📊 Predicted NQH2O Price: ${value:.2f}")
                    print(f"📈 Change from Current: ${value - features['nqh2o_lag_1']:.2f}")
                    print(f"📉 Percent Change: {((value - features['nqh2o_lag_1']) / features['nqh2o_lag_1'] * 100):.1f}%")
            else:
                print("⚠️ Could not parse JSON from response")
                print(f"Raw output: {result.stdout}")
        else:
            print("❌ No output from prediction")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Prediction failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_prediction()