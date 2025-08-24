#!/usr/bin/env python3
"""
Direct Vertex AI test WITHOUT fallback mechanisms
This test will fail if Vertex AI is not actually working
"""

import sys
import os
import json
import subprocess
import tempfile
from datetime import datetime

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def test_gcloud_auth():
    """Test if gcloud is authenticated"""
    print(f"{BLUE}Testing gcloud authentication...{NC}")
    try:
        result = subprocess.run(
            ['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            print(f"{GREEN}✅ Authenticated as: {result.stdout.strip()}{NC}")
            return True
        else:
            print(f"{RED}❌ No active gcloud authentication found{NC}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ gcloud auth check failed: {e}{NC}")
        return False
    except FileNotFoundError:
        print(f"{RED}❌ gcloud CLI not found. Please install Google Cloud SDK{NC}")
        return False

def test_project_access():
    """Test if we can access the water-futures-ai project"""
    print(f"{BLUE}Testing project access...{NC}")
    try:
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'project'],
            capture_output=True,
            text=True,
            check=True
        )
        current_project = result.stdout.strip()
        
        if current_project != "water-futures-ai":
            print(f"{YELLOW}⚠️  Current project is '{current_project}', switching to 'water-futures-ai'...{NC}")
            subprocess.run(
                ['gcloud', 'config', 'set', 'project', 'water-futures-ai'],
                check=True
            )
        
        print(f"{GREEN}✅ Project set to: water-futures-ai{NC}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Failed to access project: {e}{NC}")
        return False

def test_vertex_endpoint():
    """Test if the Vertex AI endpoint exists and is accessible"""
    print(f"{BLUE}Testing Vertex AI endpoint...{NC}")
    
    endpoint_id = "7461517903041396736"
    region = "us-central1"
    
    try:
        result = subprocess.run(
            ['gcloud', 'ai', 'endpoints', 'describe', endpoint_id, f'--region={region}', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        
        endpoint_info = json.loads(result.stdout)
        print(f"{GREEN}✅ Endpoint found: {endpoint_info.get('displayName', 'Unknown')}{NC}")
        print(f"   - State: {endpoint_info.get('deployedModels', [{}])[0].get('displayName', 'Unknown')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Failed to access endpoint: {e}{NC}")
        if e.stderr:
            print(f"   Error details: {e.stderr}")
        return False
    except json.JSONDecodeError:
        print(f"{RED}❌ Failed to parse endpoint response{NC}")
        return False

def make_direct_prediction():
    """Make a direct prediction to Vertex AI WITHOUT any fallback"""
    print(f"{BLUE}Making direct prediction to Vertex AI...{NC}")
    
    endpoint_id = "7461517903041396736"
    region = "us-central1"
    
    # Prepare test features (all 29 required features)
    features = {
        # Basin-specific features
        'Chino_Basin_eddi90d_lag_12': -0.5,
        'Mojave_Basin_pdsi_lag_12': -1.0,
        'California_Surface_Water_spi180d_lag_12': -0.8,
        'Central_Basin_eddi1y_lag_12': -0.6,
        'California_Surface_Water_spi90d_lag_12': -0.7,
        'California_Surface_Water_spei1y_lag_12': -0.9,
        
        # Drought metrics
        'drought_composite_spi': -1.5,
        'drought_composite_spei': -1.2,
        'drought_composite_pdsi': -2.0,
        'severe_drought_indicator': 1.0,
        'extreme_drought_indicator': 0.0,
        'drought_trend_4w': -0.3,
        'drought_trend_8w': -0.5,
        
        # Price features
        'nqh2o_lag_1': 400.0,
        'nqh2o_lag_2': 395.0,
        'nqh2o_lag_4': 390.0,
        'price_momentum_4w': 0.025,
        'price_momentum_8w': 0.05,
        'price_volatility_4w': 15.0,
        'price_volatility_8w': 18.0,
        'price_vs_ma_4w': 0.01,
        'price_vs_ma_12w': 0.03,
        
        # Temporal features
        'month_sin': 0.866,  # ~October
        'month_cos': -0.5,
        'week_sin': 0.707,
        'week_cos': 0.707,
        'is_drought_season': 1.0,
        'is_wet_season': 0.0,
        'time_trend': 2120.0  # Days since Jan 1, 2019
    }
    
    # Create request payload
    request_data = {"instances": [features]}
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(request_data, f)
        temp_file = f.name
    
    print(f"{YELLOW}Sending request with {len(features)} features...{NC}")
    
    try:
        # Make prediction using gcloud CLI
        result = subprocess.run(
            ['gcloud', 'ai', 'endpoints', 'predict', endpoint_id,
             f'--region={region}',
             f'--json-request={temp_file}'],
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # 30 second timeout
        )
        
        # Parse response
        output = result.stdout
        print(f"\n{BLUE}Raw response from Vertex AI:{NC}")
        print(output[:500])  # Show first 500 chars
        
        # Extract prediction value
        import re
        
        # Try to find JSON array in output
        json_match = re.search(r'\[[\d\.\-]+\]', output)
        if json_match:
            predictions = json.loads(json_match.group())
            prediction_value = predictions[0] if predictions else None
            
            print(f"\n{GREEN}✅ SUCCESSFUL VERTEX AI PREDICTION!{NC}")
            print(f"   Predicted NQH2O Price: ${prediction_value:.2f}")
            print(f"   Current Price: $400.00")
            print(f"   Change: ${prediction_value - 400:.2f} ({(prediction_value - 400) / 400 * 100:+.1f}%)")
            print(f"\n{GREEN}🎉 Vertex AI model is working correctly!{NC}")
            return True
        else:
            # Try parsing as JSON object
            try:
                response_json = json.loads(output)
                if 'predictions' in response_json:
                    prediction_value = response_json['predictions'][0]
                    print(f"\n{GREEN}✅ SUCCESSFUL VERTEX AI PREDICTION!{NC}")
                    print(f"   Predicted NQH2O Price: ${prediction_value:.2f}")
                    return True
            except:
                pass
            
            print(f"{RED}❌ Could not parse prediction from response{NC}")
            print(f"Response format not recognized")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ Request timed out after 30 seconds{NC}")
        print("The endpoint might be cold-starting or experiencing issues")
        return False
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Prediction request failed{NC}")
        print(f"Exit code: {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"{RED}❌ Unexpected error: {e}{NC}")
        return False
    finally:
        # Clean up temp file
        os.unlink(temp_file)

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}Vertex AI Direct Connection Test (NO FALLBACK){NC}")
    print(f"{BLUE}{'='*60}{NC}\n")
    
    tests_passed = []
    
    # Test 1: Check gcloud authentication
    if test_gcloud_auth():
        tests_passed.append("gcloud authentication")
    else:
        print(f"\n{RED}Cannot proceed without gcloud authentication{NC}")
        print("Please run: gcloud auth login")
        return 1
    
    print()
    
    # Test 2: Check project access
    if test_project_access():
        tests_passed.append("project access")
    else:
        print(f"\n{RED}Cannot access water-futures-ai project{NC}")
        return 1
    
    print()
    
    # Test 3: Check endpoint exists
    if test_vertex_endpoint():
        tests_passed.append("endpoint access")
    else:
        print(f"\n{YELLOW}⚠️  Endpoint might not be deployed or accessible{NC}")
    
    print()
    
    # Test 4: Make actual prediction
    if make_direct_prediction():
        tests_passed.append("prediction")
    else:
        print(f"\n{RED}Direct prediction failed - Vertex AI model is NOT working{NC}")
        return 1
    
    # Summary
    print(f"\n{BLUE}{'='*60}{NC}")
    print(f"{BLUE}Test Summary{NC}")
    print(f"{BLUE}{'='*60}{NC}")
    
    if len(tests_passed) == 4:
        print(f"{GREEN}✅ ALL TESTS PASSED!{NC}")
        print(f"{GREEN}The Vertex AI model is fully operational.{NC}")
        return 0
    else:
        print(f"{YELLOW}Tests passed: {len(tests_passed)}/4{NC}")
        for test in tests_passed:
            print(f"  ✅ {test}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)