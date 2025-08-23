# NQH2O Forecasting Model - Vertex AI Deployment Guide

## Overview
This package contains a complete machine learning solution for forecasting the Nasdaq Veles California Water Index (NQH2O) using drought data from Google Earth Engine GRIDMET dataset.

## Model Performance
- **Best Model**: Gradient Boosting Regressor
- **Test RMSE**: $90.64
- **Test MAE**: $86.13
- **Features**: 29 engineered features including drought indices and price lags
- **Training Period**: 2019-2022
- **Validation Period**: 2023
- **Test Period**: 2024-2025

## Architecture
- **Ensemble Approach**: 5 models (Ridge, Lasso, Elastic Net, Random Forest, Gradient Boosting)
- **Feature Engineering**: Drought composites, price lags, temporal features
- **Preprocessing**: StandardScaler + SelectKBest feature selection
- **Deployment**: Custom container on Vertex AI

## Files Structure
```
nqh2o_prediction_service/
├── Dockerfile                    # Container definition
├── predictor.py                  # Main prediction service
├── requirements.txt              # Python dependencies
├── build_and_push.sh            # Build and push script
├── deploy.sh                     # Deployment script
├── client_example.py             # Usage example
├── monitoring_config.json        # Monitoring configuration
├── nqh2o_model_*.joblib         # Trained models
├── nqh2o_scalers.joblib         # Preprocessing scalers
├── nqh2o_feature_selector.joblib # Feature selector
├── nqh2o_ensemble_weights.joblib # Ensemble weights
└── nqh2o_feature_names.txt      # Feature names
```

## Deployment Steps

### 1. Prerequisites
- Google Cloud Project with Vertex AI API enabled
- Docker installed and configured
- gcloud CLI installed and authenticated
- Appropriate IAM permissions

### 2. Configuration
Update the following variables in the deployment scripts:
- PROJECT_ID: Your Google Cloud project ID
- REGION: Deployment region (e.g., us-central1)
- MODEL_NAME: Name for your model
- ENDPOINT_NAME: Name for your endpoint

### 3. Build and Push Container
```bash
./build_and_push.sh
```

### 4. Deploy to Vertex AI
```bash
./deploy.sh
```

### 5. Test Deployment
```python
python client_example.py
```

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status and model loading status.

### Prediction
```
POST /predict
Content-Type: application/json

{
  "instances": [
    {
      "nqh2o_lag_1": 400.0,
      "nqh2o_lag_2": 395.0,
      "time_trend": 1000.0,
      "drought_composite_spi": -1.5,
      ...
    }
  ]
}
```

### Response Format
```json
{
  "predictions": [425.67],
  "individual_predictions": {
    "gradient_boosting": [425.67],
    "random_forest": [428.34],
    ...
  },
  "model_version": "1.0",
  "timestamp": "2025-01-23T18:53:00"
}
```

## Feature Requirements
The model requires 29 features:
1. **Price Lags**: nqh2o_lag_1, nqh2o_lag_2, nqh2o_lag_4
2. **Drought Composites**: drought_composite_spi, drought_composite_spei, drought_composite_pdsi
3. **Drought Indicators**: severe_drought_indicator, extreme_drought_indicator
4. **Trends**: time_trend, drought_trend_4w, drought_trend_8w
5. **Price Features**: price_momentum_4w, price_momentum_8w, price_volatility_4w, price_volatility_8w
6. **Technical Indicators**: price_vs_ma_4w, price_vs_ma_12w
7. **Seasonal Features**: month_sin, month_cos, week_sin, week_cos
8. **Calendar Features**: is_drought_season, is_wet_season
9. **Lagged Drought Features**: Various basin-specific drought indices with 12-week lags

## Monitoring and Maintenance

### Model Monitoring
- Prediction drift detection enabled
- Explanation logging for interpretability
- Performance metrics tracking
- Automated alerting on degradation

### Retraining Triggers
- Monthly performance evaluation
- Significant drift detection
- New drought events or market regime changes
- Quarterly model updates with new data

### Scaling Configuration
- **Machine Type**: n1-standard-2
- **Min Replicas**: 1
- **Max Replicas**: 3
- **Auto-scaling**: Based on CPU utilization and request rate

## Cost Optimization
- Use preemptible instances for batch predictions
- Scale down during low-usage periods
- Monitor prediction request patterns
- Consider regional deployment for latency optimization

## Security Considerations
- IAM-based access control
- VPC-native networking
- Audit logging enabled
- Model artifact encryption
- API authentication required

## Troubleshooting

### Common Issues
1. **Container Build Failures**: Check Dockerfile and dependencies
2. **Model Loading Errors**: Verify artifact paths and permissions
3. **Prediction Errors**: Validate input feature format and values
4. **Scaling Issues**: Monitor resource utilization and adjust limits

### Debugging
- Check Cloud Logging for detailed error messages
- Use health endpoint to verify model loading
- Test with example client before production use
- Monitor prediction latency and accuracy

## Support and Maintenance
- Model version: 1.0
- Last updated: 2025-08-23
- Contact: ML Engineering Team
- Documentation: This README and inline code comments
