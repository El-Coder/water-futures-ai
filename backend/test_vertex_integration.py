#!/usr/bin/env python3
"""
Test script to verify backend integration with Vertex AI NQH2O model
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.nqh2o_prediction_service import get_prediction_service
from services.forecast_service_updated import forecast_service
import json
from datetime import datetime

def test_direct_nqh2o_service():
    """Test direct NQH2O prediction service"""
    print("=" * 60)
    print("Testing Direct NQH2O Prediction Service")
    print("=" * 60)
    
    service = get_prediction_service()
    
    # Test data
    drought_metrics = {
        'spi': -1.5,
        'spei': -1.2,
        'pdsi': -2.0,
        'severity': 2,
        'trend_4w': -0.5,
        'trend_8w': -0.8
    }
    
    price_history = [380, 385, 390, 388, 392, 395, 398, 400, 402, 405, 403, 400]
    
    print("\nInput Data:")
    print(f"  Current Price: ${price_history[-1]}")
    print(f"  Drought SPI: {drought_metrics['spi']}")
    print(f"  Drought Severity: {drought_metrics['severity']}")
    
    # Make prediction
    result = service.predict(
        drought_metrics=drought_metrics,
        price_history=price_history,
        basin_data=None
    )
    
    print("\nPrediction Result:")
    if result.get('success'):
        print(f"  ✅ Status: SUCCESS")
        print(f"  📊 Predicted Price: ${result['prediction']:.2f}")
        print(f"  📈 Price Change: ${result['price_change']:.2f} ({result['price_change_pct']:.1f}%)")
        print(f"  🎯 Confidence: {result['confidence']:.0f}%")
        print(f"  🔖 Model Version: {result['model_version']}")
        
        # Get explanation
        explanation = service.get_forecast_explanation(result)
        print(f"\n  📝 Explanation: {explanation}")
    else:
        print(f"  ❌ Status: FAILED")
        print(f"  Error: {result.get('error', 'Unknown error')}")
    
    return result

async def test_forecast_service():
    """Test the updated forecast service"""
    print("\n" + "=" * 60)
    print("Testing Forecast Service with Vertex AI")
    print("=" * 60)
    
    # Test forecast generation
    result = await forecast_service.generate_forecast(
        contract_code="NQH25",
        horizon_days=7,
        include_confidence=True
    )
    
    print("\nForecast Service Result:")
    print(f"  Contract: {result['contract_code']}")
    print(f"  Current Price: ${result['current_price']:.2f}")
    print(f"  Using Vertex AI: {result.get('using_vertex_ai', False)}")
    print(f"  Model Confidence: {result['model_confidence']*100:.0f}%")
    
    print("\n  7-Day Forecast:")
    for pred in result['predicted_prices'][:3]:  # Show first 3 days
        print(f"    {pred['day']}: ${pred['price']:.2f}")
    print(f"    ... (showing 3 of {len(result['predicted_prices'])} days)")
    
    if result.get('factors', {}).get('explanation'):
        print(f"\n  Explanation: {result['factors']['explanation']}")
    
    return result

async def test_trading_signals():
    """Test trading signal generation"""
    print("\n" + "=" * 60)
    print("Testing Trading Signals")
    print("=" * 60)
    
    signals = await forecast_service.get_trading_signals()
    
    print(f"\nGenerated {signals['total_signals']} trading signals:")
    
    for signal in signals['signals']:
        emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal['signal'], "⚪")
        print(f"\n  {emoji} {signal['contract_code']}:")
        print(f"     Signal: {signal['signal']} ({signal['strength']})")
        print(f"     Current: ${signal['current_price']:.2f}")
        print(f"     Target: ${signal['target_price']:.2f}")
        print(f"     Expected Return: {signal['expected_return']:.1f}%")
        print(f"     Confidence: {signal['confidence']:.0f}%")
        print(f"     Model: {signal['model']}")
    
    return signals

async def test_model_accuracy():
    """Test model accuracy reporting"""
    print("\n" + "=" * 60)
    print("Model Performance Metrics")
    print("=" * 60)
    
    accuracy = await forecast_service.get_forecast_accuracy()
    
    print("\nNQH2O Model Performance:")
    print(f"  📊 RMSE: ${accuracy['rmse']:.2f}")
    print(f"  📈 MAE: ${accuracy['mae']:.2f}")
    print(f"  🎯 R² Score: {accuracy['r2']:.2f}")
    print(f"  ✅ Accuracy: {accuracy['accuracy_rate']*100:.0f}%")
    print(f"  🔬 Model: {accuracy['model']}")
    print(f"  📅 Test Period: {accuracy['period']}")
    print(f"  📝 Sample Size: {accuracy['sample_size']} days")
    
    return accuracy

async def main():
    """Run all tests"""
    print("\n🚀 Starting Vertex AI Integration Tests\n")
    
    try:
        # Test 1: Direct service
        direct_result = test_direct_nqh2o_service()
        
        # Test 2: Forecast service
        forecast_result = await test_forecast_service()
        
        # Test 3: Trading signals
        signals_result = await test_trading_signals()
        
        # Test 4: Model accuracy
        accuracy_result = await test_model_accuracy()
        
        print("\n" + "=" * 60)
        print("✅ All Tests Complete!")
        print("=" * 60)
        
        # Summary
        print("\nIntegration Summary:")
        print(f"  • Direct NQH2O Service: {'✅ Working' if direct_result.get('success') else '❌ Failed'}")
        print(f"  • Forecast Service: {'✅ Working' if forecast_result else '❌ Failed'}")
        print(f"  • Trading Signals: {'✅ Generated' if signals_result['total_signals'] > 0 else '❌ None'}")
        print(f"  • Model Accuracy: ✅ RMSE ${accuracy_result['rmse']:.2f}")
        
        if forecast_result.get('using_vertex_ai'):
            print("\n🎉 Vertex AI integration is fully operational!")
        else:
            print("\n⚠️ Using fallback model (Vertex AI not connected)")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)