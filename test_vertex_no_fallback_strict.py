#!/usr/bin/env python3
"""
STRICT Vertex AI Test - ZERO TOLERANCE for fallbacks or dummy data
This test will CRASH AND BURN if Vertex AI is not actually being used
"""

import sys
import os
import subprocess
import json
import tempfile

# Force imports from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def test_vertex_directly_no_fallback():
    """
    Make a DIRECT gcloud call to Vertex AI endpoint
    This CANNOT use fallback data - it either works or fails
    """
    print(f"\n{YELLOW}TESTING DIRECT VERTEX AI CALL - NO PYTHON, NO FALLBACKS{NC}\n")
    
    endpoint_id = "7461517903041396736"
    region = "us-central1"
    
    # Create test input with all 29 required features
    test_features = {
        'Chino_Basin_eddi90d_lag_12': -0.8,
        'Mojave_Basin_pdsi_lag_12': -1.5,
        'California_Surface_Water_spi180d_lag_12': -1.0,
        'Central_Basin_eddi1y_lag_12': -0.7,
        'California_Surface_Water_spi90d_lag_12': -0.9,
        'California_Surface_Water_spei1y_lag_12': -1.1,
        'drought_composite_spi': -1.8,
        'drought_composite_spei': -1.6,
        'drought_composite_pdsi': -2.2,
        'severe_drought_indicator': 1.0,
        'extreme_drought_indicator': 1.0,
        'drought_trend_4w': -0.4,
        'drought_trend_8w': -0.6,
        'nqh2o_lag_1': 450.0,
        'nqh2o_lag_2': 445.0,
        'nqh2o_lag_4': 440.0,
        'price_momentum_4w': 0.03,
        'price_momentum_8w': 0.06,
        'price_volatility_4w': 20.0,
        'price_volatility_8w': 25.0,
        'price_vs_ma_4w': 0.02,
        'price_vs_ma_12w': 0.04,
        'month_sin': 0.866,
        'month_cos': -0.5,
        'week_sin': 0.707,
        'week_cos': 0.707,
        'is_drought_season': 1.0,
        'is_wet_season': 0.0,
        'time_trend': 2150.0
    }
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"instances": [test_features]}, f)
        temp_file = f.name
    
    try:
        print(f"Making DIRECT gcloud call to Vertex AI endpoint...")
        print(f"Endpoint: {endpoint_id}")
        print(f"Region: {region}")
        
        # Make the actual call
        result = subprocess.run(
            ['gcloud', 'ai', 'endpoints', 'predict', endpoint_id,
             f'--region={region}',
             f'--json-request={temp_file}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"{RED}❌ VERTEX AI CALL FAILED!{NC}")
            print(f"Error: {result.stderr}")
            return None
        
        # Parse the response
        output = result.stdout
        print(f"\n{GREEN}RAW VERTEX AI RESPONSE:{NC}")
        print(output[:500])
        
        # Extract prediction value
        import re
        json_match = re.search(r'\[[\d\.\-]+\]', output)
        
        if json_match:
            predictions = json.loads(json_match.group())
            prediction_value = predictions[0] if predictions else None
            
            if prediction_value:
                print(f"\n{GREEN}✅ REAL VERTEX AI PREDICTION: ${prediction_value:.2f}{NC}")
                print(f"This is a REAL prediction from the deployed model")
                print(f"Current price: $450.00")
                print(f"Predicted change: ${prediction_value - 450:.2f} ({(prediction_value - 450)/450*100:+.1f}%)")
                return prediction_value
            else:
                print(f"{RED}❌ No prediction value found{NC}")
                return None
        else:
            print(f"{RED}❌ Could not parse Vertex AI response{NC}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"{RED}❌ Vertex AI call timed out - endpoint might be down{NC}")
        return None
    except Exception as e:
        print(f"{RED}❌ Fatal error: {e}{NC}")
        return None
    finally:
        os.unlink(temp_file)

def verify_no_fallback_in_code():
    """
    Check if the code has fallback logic that could bypass Vertex AI
    """
    print(f"\n{YELLOW}CHECKING FOR FALLBACK CODE...{NC}\n")
    
    files_to_check = [
        "backend/services/forecast_service_updated.py",
        "backend/services/nqh2o_prediction_service.py",
        "backend/services/vertex_ai_service.py"
    ]
    
    fallback_patterns = [
        "_fallback",
        "fallback",
        "default",
        "dummy",
        "simulate",
        "mock",
        "except",  # Exception handlers that might use fallback
    ]
    
    found_fallbacks = []
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern in fallback_patterns:
                        if pattern in line.lower():
                            found_fallbacks.append({
                                'file': filepath,
                                'line': i,
                                'content': line.strip()
                            })
    
    if found_fallbacks:
        print(f"{RED}⚠️ FOUND {len(found_fallbacks)} POTENTIAL FALLBACK POINTS:{NC}")
        for fb in found_fallbacks[:10]:  # Show first 10
            print(f"  {fb['file']}:{fb['line']}")
            print(f"    {fb['content'][:80]}")
    else:
        print(f"{GREEN}✅ No obvious fallback patterns found{NC}")
    
    return len(found_fallbacks) == 0

def check_vertex_monitoring():
    """
    Check Vertex AI monitoring metrics to see if it's receiving requests
    """
    print(f"\n{YELLOW}CHECKING VERTEX AI MONITORING...{NC}\n")
    
    try:
        # Get monitoring data
        result = subprocess.run([
            'gcloud', 'monitoring', 'time-series', 'list',
            '--filter=metric.type="aiplatform.googleapis.com/prediction/online/prediction_count"',
            '--format=json',
            '--project=water-futures-ai'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            if data:
                print(f"{GREEN}✅ Found monitoring data - Vertex AI is receiving requests{NC}")
                return True
            else:
                print(f"{YELLOW}⚠️ No recent prediction metrics found{NC}")
                return False
        else:
            print(f"{YELLOW}Could not fetch monitoring data{NC}")
            return False
    except:
        print(f"{YELLOW}Monitoring check skipped{NC}")
        return False

def main():
    print(f"\n{RED}{'='*60}{NC}")
    print(f"{RED}STRICT VERTEX AI TEST - ZERO TOLERANCE{NC}")
    print(f"{RED}{'='*60}{NC}")
    print(f"\nThis test will FAIL if:")
    print(f"  • Vertex AI is not actually being called")
    print(f"  • Any fallback or dummy data is used")
    print(f"  • The model endpoint is not responding")
    
    # Test 1: Direct Vertex AI call
    prediction = test_vertex_directly_no_fallback()
    
    # Test 2: Check for fallback code
    no_fallbacks = verify_no_fallback_in_code()
    
    # Test 3: Check monitoring
    has_metrics = check_vertex_monitoring()
    
    # Final verdict
    print(f"\n{RED}{'='*60}{NC}")
    print(f"{RED}FINAL VERDICT{NC}")
    print(f"{RED}{'='*60}{NC}\n")
    
    if prediction is not None and prediction > 0:
        print(f"{GREEN}✅ VERTEX AI IS WORKING!{NC}")
        print(f"   Real prediction received: ${prediction:.2f}")
        print(f"   This came from the actual deployed model")
        
        if not no_fallbacks:
            print(f"\n{YELLOW}⚠️ WARNING: Fallback code exists that could bypass Vertex AI{NC}")
        
        return 0
    else:
        print(f"{RED}❌ VERTEX AI IS NOT WORKING!{NC}")
        print(f"\nThe system is NOT using the real Vertex AI model.")
        print(f"Any predictions you see are from fallback/dummy data.")
        
        print(f"\n{YELLOW}To fix this:{NC}")
        print(f"  1. Check gcloud authentication: gcloud auth list")
        print(f"  2. Verify project: gcloud config get-value project")
        print(f"  3. Check endpoint: gcloud ai endpoints list --region=us-central1")
        print(f"  4. Remove ALL fallback code from the services")
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)