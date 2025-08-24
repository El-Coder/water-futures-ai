#!/usr/bin/env python3
"""
Direct test of Vertex AI endpoint using gcloud authentication
"""

import json
import subprocess
import math
from datetime import datetime

def test_vertex_ai_directly():
    """Test Vertex AI endpoint directly using gcloud"""
    
    print("Testing Vertex AI NQH2O Model")
    print("=" * 50)
    
    # Prepare all 29 features
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
    request = {"instances": [features]}
    
    # Save to temp file
    with open('/tmp/test_request.json', 'w') as f:
        json.dump(request, f)
    
    print("Input Features:")
    print(f"  Current Price: ${features['nqh2o_lag_1']}")
    print(f"  Drought SPI: {features['drought_composite_spi']}")
    print(f"  Severe Drought: {'Yes' if features['severe_drought_indicator'] else 'No'}")
    print()
    
    # Call Vertex AI using gcloud
    try:
        result = subprocess.run([
            'gcloud', 'ai', 'endpoints', 'predict',
            '7461517903041396736',
            '--region=us-central1',
            '--json-request=/tmp/test_request.json'
        ], capture_output=True, text=True, check=True)
        
        if result.stdout:
            # Parse the response
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('[') or line.strip().startswith('{'):
                    json_lines = []
                    for j in range(i, len(lines)):
                        json_lines.append(lines[j])
                        if lines[j].strip().endswith(']') or lines[j].strip().endswith('}'):
                            break
                    json_str = '\n'.join(json_lines)
                    break
            
            response = json.loads(json_str)
            
            # Extract prediction
            if isinstance(response, list) and len(response) > 0:
                prediction = response[0]
                
                print("✅ Vertex AI Response:")
                print(f"  Predicted Price: ${prediction:.2f}")
                print(f"  Change from Current: ${prediction - features['nqh2o_lag_1']:.2f}")
                print(f"  Percent Change: {((prediction - features['nqh2o_lag_1']) / features['nqh2o_lag_1'] * 100):.1f}%")
                
                return True, prediction
            else:
                print("❌ Unexpected response format")
                return False, None
                
    except subprocess.CalledProcessError as e:
        print(f"❌ gcloud command failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False, None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False, None

def create_prediction_function():
    """Create a Python function that uses subprocess to call Vertex AI"""
    
    print("\n" + "=" * 50)
    print("Creating Backend Integration Function")
    print("=" * 50)
    
    code = '''
def predict_with_gcloud(features_dict):
    """
    Make prediction using gcloud CLI
    This avoids authentication issues with the Python client
    """
    import subprocess
    import json
    import tempfile
    
    # Create temporary file for request
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"instances": [features_dict]}, f)
        temp_file = f.name
    
    try:
        # Call gcloud
        result = subprocess.run([
            'gcloud', 'ai', 'endpoints', 'predict',
            '7461517903041396736',
            '--region=us-central1',
            f'--json-request={temp_file}'
        ], capture_output=True, text=True, check=True)
        
        # Parse response
        output = result.stdout
        # Extract JSON from output
        import re
        json_match = re.search(r'\\[.*\\]', output, re.DOTALL)
        if json_match:
            predictions = json.loads(json_match.group())
            return {"success": True, "prediction": predictions[0]}
        else:
            return {"success": False, "error": "Could not parse response"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        import os
        os.unlink(temp_file)
'''
    
    print("Function created for backend integration:")
    print(code)
    
    return code

if __name__ == "__main__":
    # Test direct connection
    success, prediction = test_vertex_ai_directly()
    
    if success:
        print("\n✅ Vertex AI endpoint is working!")
        print("The backend can use gcloud CLI for predictions to avoid auth issues")
        
        # Show integration function
        create_prediction_function()
    else:
        print("\n❌ Could not connect to Vertex AI endpoint")
        print("Please check:")
        print("  1. gcloud is authenticated: gcloud auth login")
        print("  2. Project is set: gcloud config set project water-futures-ai")
        print("  3. Endpoint is deployed and active")