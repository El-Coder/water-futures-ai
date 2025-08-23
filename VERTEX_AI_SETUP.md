# Vertex AI Integration for Water Futures

## How the Backend Talks to Vertex AI

### Architecture Overview

```
Frontend (React) 
    ↓ API Request
Backend (FastAPI)
    ↓ Forecast Request
VertexAIService (vertex_ai_service.py)
    ↓ Feature Preparation
Vertex AI Model Endpoint
    ↓ ML Prediction
Response with Forecast
```

### Key Components

1. **VertexAIService** (`backend/services/vertex_ai_service.py`)
   - Handles all communication with Vertex AI
   - Prepares features (drought severity, precipitation, historical prices)
   - Makes predictions using deployed model endpoint
   - Falls back to simple model if Vertex AI unavailable

2. **API Endpoint** (`backend/main_simple.py`)
   - `/api/v1/forecasts/predict` endpoint
   - Collects historical data from data store
   - Calls `vertex_ai_service.predict()` with features
   - Returns formatted forecast response

3. **Vertex AI Model**
   - AutoML Tabular model trained on historical water futures data
   - Takes inputs: drought_severity, precipitation, historical_prices, region
   - Returns: price predictions for next 7 days with confidence intervals

### Data Flow

1. **User requests forecast** from frontend
2. **Backend receives request** with contract code and horizon
3. **Backend prepares features**:
   ```python
   features = {
       "contract_code": "NQH25",
       "current_price": 508.23,
       "drought_severity": 4,  # From drought monitoring data
       "precipitation": 35,     # From weather data
       "region": "Central Valley",
       "historical_prices": [505, 506, 507, 508...]  # Last 30 days
   }
   ```

4. **VertexAIService sends to Vertex AI**:
   - If model deployed: Uses Vertex AI endpoint
   - If not deployed: Uses fallback simple model

5. **Vertex AI returns predictions**:
   ```json
   {
       "predicted_prices": [
           {"date": "Day 1", "price": 510.5},
           {"date": "Day 2", "price": 512.3},
           ...
       ],
       "confidence_intervals": {
           "upper": [515, 517, ...],
           "lower": [506, 507, ...]
       },
       "model_confidence": 0.82
   }
   ```

### Setting Up Vertex AI (For Production)

1. **Enable APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

2. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create water-futures-ml \
       --display-name="Water Futures ML Service"
   
   gcloud projects add-iam-policy-binding water-futures-ai \
       --member="serviceAccount:water-futures-ml@water-futures-ai.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"
   ```

3. **Train and Deploy Model**:
   ```bash
   cd backend
   python train_model.py
   ```

4. **Set Environment Variables**:
   ```bash
   export VERTEX_ENDPOINT_NAME="water-futures-endpoint"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

### Hackathon Simplification

For the hackathon, the system works with or without Vertex AI:

- **With Vertex AI**: Full ML predictions using AutoML model
- **Without Vertex AI**: Simple fallback model using drought severity multiplier

The fallback model (`_simple_forecast` method) provides reasonable predictions:
- Base price × drought multiplier (2% per severity level above 3)
- Adds realistic noise and trend
- Returns same format as Vertex AI

### Key Features Used from Vertex AI

1. **AutoML Tabular**: Automated model training for regression
2. **Model Endpoints**: Serverless prediction serving
3. **Feature Store** (optional): Store embeddings for regions
4. **Batch Prediction** (optional): Process multiple forecasts

### Cost Optimization for Hackathon

- Use `n1-standard-4` machines (cheaper than GPU)
- Set `min_replica_count=1` to avoid idle costs
- Use AutoML with minimum budget (1000 milli-node-hours)
- Fallback model means Vertex AI is optional

### Testing Without Vertex AI

The backend automatically falls back to simple forecasting if:
- No Vertex AI endpoint configured
- API calls fail
- Running locally without GCP credentials

This ensures the hackathon demo works regardless of cloud setup!