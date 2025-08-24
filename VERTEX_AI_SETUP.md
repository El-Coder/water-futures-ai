# Vertex AI Integration for Water Futures

## 🚀 Production NQH2O Model Deployed!

**Status**: ✅ FULLY DEPLOYED AND OPERATIONAL
- **Endpoint ID**: `7461517903041396736`
- **Model ID**: `5834566149374738432`
- **Container**: `gcr.io/water-futures-ai/nqh2o-predictor`
- **Performance**: $90.64 RMSE (Gradient Boosting)

## How the Backend Talks to Vertex AI

### Architecture Overview

```
Frontend (React) 
    ↓ API Request
Backend (FastAPI)
    ↓ Forecast Request
NQH2OPredictionService (nqh2o_prediction_service.py)
    ↓ Feature Engineering (29 features)
Vertex AI Model Endpoint (5 ensemble models)
    ↓ ML Prediction
Response with NQH2O Price Forecast
```

### Key Components

1. **NQH2OPredictionService** (`backend/services/nqh2o_prediction_service.py`)
   - Production-ready service for NQH2O predictions
   - Automatically prepares all 29 required features
   - Handles drought metrics, price history, and temporal features
   - Returns predictions with confidence scores

2. **Deployed Models** (Ensemble of 5)
   - **Gradient Boosting** (Best: RMSE $90.64)
   - Random Forest
   - Ridge Regression
   - Lasso
   - Elastic Net

3. **API Integration**
   ```python
   from backend.services.nqh2o_prediction_service import get_prediction_service
   
   service = get_prediction_service()
   result = service.predict(
       drought_metrics={'spi': -1.5, 'severity': 2},
       price_history=[390, 395, 400],
       basin_data=None  # Optional
   )
   ```

### Required Features (29 Total)

The model automatically engineers these from your input:

#### Input Data Needed:
1. **Drought Metrics**
   - `spi`: Standardized Precipitation Index
   - `spei`: Standardized Precipitation-Evapotranspiration Index
   - `pdsi`: Palmer Drought Severity Index
   - `severity`: 0-4 scale (0=none, 4=exceptional)

2. **Price History**
   - Recent NQH2O prices (at least 4 weeks)

3. **Basin Data** (Optional)
   - Basin-specific drought indicators
   - Will use defaults if not provided

### Live Prediction Example

```python
# Current test shows model is working:
# Input: Severe drought (SPI: -1.5), Current price: $400
# Output: Predicted price: $470.81 (+17.7%)
```

### Data Flow

1. **User requests forecast** from frontend
2. **Backend collects data**:
   - Current drought conditions from monitoring services
   - Historical NQH2O prices from data store
   - Temporal features (automatically calculated)

3. **NQH2OPredictionService prepares features**:
   ```python
   features = service.prepare_features(
       drought_metrics={
           'spi': -1.5,
           'spei': -1.2,
           'pdsi': -2.0,
           'severity': 2,
           'trend_4w': -0.5,
           'trend_8w': -0.8
       },
       price_history=[380, 385, 390, 395, 400],
       basin_data=None  # Uses defaults
   )
   ```

4. **Vertex AI returns prediction**:
   ```json
   {
       "success": true,
       "prediction": 470.81,
       "confidence": 85,
       "price_change": 70.81,
       "price_change_pct": 17.7,
       "drought_severity": 2,
       "model_version": "1.0"
   }
   ```

### Testing the Deployed Model

```bash
# Direct test with gcloud
python nqh2o_prediction_service/test_direct.py

# Test with multiple scenarios
python nqh2o_prediction_service/test_deployment.py

# Integration test
python nqh2o_prediction_service/integration_example.py
```

### Cost Optimization

- **Current Setup**: `n1-standard-2` machines
- **Auto-scaling**: 1-3 replicas based on load
- **Estimated Cost**: $50-150/month
- **Latency**: <2 seconds per prediction

### Model Performance Metrics

| Model | RMSE | MAE | R² |
|-------|------|-----|-----|
| **Gradient Boosting** | **$90.64** | **$86.13** | **0.82** |
| Random Forest | $92.45 | $87.29 | 0.81 |
| Ridge | $94.12 | $88.67 | 0.79 |
| Lasso | $95.23 | $89.14 | 0.78 |
| Elastic Net | $94.87 | $88.92 | 0.79 |

### Environment Variables

```bash
# Already configured in deployment
export PROJECT_ID="water-futures-ai"
export REGION="us-central1"
export ENDPOINT_ID="7461517903041396736"
export MODEL_ID="5834566149374738432"
```

### Monitoring & Maintenance

1. **Check Model Status**:
   ```bash
   gcloud ai endpoints describe 7461517903041396736 \
       --region=us-central1 \
       --format="value(deployedModels[].displayName)"
   ```

2. **View Predictions Logs**:
   ```bash
   gcloud logging read \
       "resource.type=aiplatform.googleapis.com/Endpoint AND \
        resource.labels.endpoint_id=7461517903041396736" \
       --limit=10
   ```

3. **Monitor Performance**:
   - Cloud Console → Vertex AI → Endpoints
   - Check latency, error rates, and utilization

### Fallback Mechanism

The service includes automatic fallback if Vertex AI is unavailable:
- Uses simple drought severity multiplier
- Maintains same API interface
- Ensures demo reliability

### Key Advantages of Deployed Model

1. **Production-Ready**: Fully containerized and deployed
2. **Ensemble Approach**: Combines 5 models for robustness
3. **Feature Engineering**: Automatic feature preparation
4. **Real Training Data**: Trained on 2019-2024 NQH2O prices
5. **Drought Integration**: Uses GRIDMET drought data
6. **Confidence Scores**: Provides prediction confidence

### Next Steps

1. ✅ Model deployed and operational
2. ✅ Integration service created
3. ⏳ Monitor initial predictions
4. 📊 Set up dashboards for tracking
5. 🔄 Schedule monthly retraining

### Support

- **Model Version**: 1.0
- **Last Deployed**: 2025-08-23
- **Training Period**: 2019-2024
- **Test RMSE**: $90.64
- **Container**: `gcr.io/water-futures-ai/nqh2o-predictor`