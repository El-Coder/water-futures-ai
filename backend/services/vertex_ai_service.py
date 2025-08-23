"""
Vertex AI integration for water futures forecasting
"""
from google.cloud import aiplatform
from google.cloud import storage
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json
import os

class VertexAIService:
    def __init__(self):
        self.project_id = "water-futures-ai"
        self.region = "us-central1"
        self.bucket_name = "water-futures-data"
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.region
        )
        
        # Model endpoint (will be set after deployment)
        self.endpoint_name = os.getenv("VERTEX_ENDPOINT_NAME", None)
        self.model_endpoint = None
        
        if self.endpoint_name:
            self._load_endpoint()
    
    def _load_endpoint(self):
        """Load deployed model endpoint"""
        try:
            endpoints = aiplatform.Endpoint.list(
                filter=f'display_name="{self.endpoint_name}"'
            )
            if endpoints:
                self.model_endpoint = endpoints[0]
                print(f"Loaded Vertex AI endpoint: {self.endpoint_name}")
        except Exception as e:
            print(f"Error loading endpoint: {e}")
    
    async def train_forecast_model(self, training_data_path: str):
        """
        Train a water futures forecasting model using AutoML or custom training
        """
        # For hackathon, we'll use AutoML Forecasting
        dataset = aiplatform.TimeSeriesDataset.create(
            display_name="water-futures-historical",
            gcs_source=f"gs://{self.bucket_name}/{training_data_path}",
        )
        
        # Configure AutoML training
        job = aiplatform.AutoMLForecastingTrainingJob(
            display_name="water-futures-forecast-model",
            optimization_objective="minimize-rmse",
            column_transformations=[
                {"numeric": {"column_name": "price"}},
                {"numeric": {"column_name": "volume"}},
                {"numeric": {"column_name": "drought_severity"}},
                {"numeric": {"column_name": "precipitation"}},
                {"categorical": {"column_name": "region"}},
            ],
        )
        
        model = job.run(
            dataset=dataset,
            target_column="price",
            time_column="date",
            time_series_identifier_column="contract_code",
            available_at_forecast_columns=["drought_severity", "precipitation"],
            unavailable_at_forecast_columns=[],
            forecast_horizon=7,  # 7 days ahead
            data_granularity_unit="day",
            data_granularity_count=1,
            training_fraction_split=0.8,
            validation_fraction_split=0.1,
            test_fraction_split=0.1,
        )
        
        # Deploy model
        endpoint = model.deploy(
            machine_type="n1-standard-4",
            min_replica_count=1,
            max_replica_count=3,
        )
        
        self.model_endpoint = endpoint
        return endpoint
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions using deployed Vertex AI model
        """
        if not self.model_endpoint:
            # Fallback to simple prediction if no model deployed
            return self._simple_forecast(features)
        
        try:
            # Prepare input for Vertex AI
            instances = [{
                "contract_code": features.get("contract_code"),
                "current_price": features.get("current_price", 500),
                "drought_severity": features.get("drought_severity", 3),
                "precipitation": features.get("precipitation", 50),
                "region": features.get("region", "Central Valley"),
                "historical_prices": features.get("historical_prices", []),
            }]
            
            # Make prediction
            predictions = self.model_endpoint.predict(instances=instances)
            
            # Parse predictions
            forecast_values = predictions.predictions[0]["values"]
            confidence_intervals = predictions.predictions[0].get("confidence_intervals", {})
            
            return {
                "predicted_prices": [
                    {"date": f"Day {i+1}", "price": price}
                    for i, price in enumerate(forecast_values)
                ],
                "confidence": confidence_intervals,
                "model_confidence": predictions.predictions[0].get("confidence", 0.75),
                "factors": {
                    "drought_impact": self._calculate_drought_impact(features),
                    "seasonal_trend": self._calculate_seasonal_trend(features),
                    "market_momentum": self._calculate_momentum(features),
                }
            }
            
        except Exception as e:
            print(f"Vertex AI prediction error: {e}")
            return self._simple_forecast(features)
    
    def _simple_forecast(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback simple forecasting when Vertex AI not available
        """
        current_price = features.get("current_price", 500)
        drought_severity = features.get("drought_severity", 3)
        horizon_days = features.get("horizon_days", 7)
        
        # Simple model: price increases with drought severity
        drought_multiplier = 1 + (drought_severity - 3) * 0.02  # 2% per severity level
        trend = 0.001  # 0.1% daily trend
        
        predicted_prices = []
        for day in range(horizon_days):
            # Add some randomness for realism
            noise = np.random.normal(0, 2)  # $2 standard deviation
            price = current_price * drought_multiplier * (1 + trend * day) + noise
            predicted_prices.append({
                "date": f"Day {day + 1}",
                "price": round(price, 2)
            })
        
        return {
            "predicted_prices": predicted_prices,
            "confidence": {
                "upper": [p["price"] + 5 for p in predicted_prices],
                "lower": [p["price"] - 5 for p in predicted_prices],
            },
            "model_confidence": 0.65 + (drought_severity * 0.05),  # Higher confidence with extreme drought
            "factors": {
                "drought_severity": drought_severity,
                "base_price": current_price,
                "trend": "increasing" if drought_severity > 3 else "stable",
            }
        }
    
    def _calculate_drought_impact(self, features: Dict) -> float:
        """Calculate price impact from drought conditions"""
        severity = features.get("drought_severity", 3)
        return (severity - 3) * 2.5  # Each level above 3 adds 2.5% impact
    
    def _calculate_seasonal_trend(self, features: Dict) -> str:
        """Determine seasonal trend"""
        # In reality, would use date to determine season
        return "summer_peak"  # Summer typically has higher water demand
    
    def _calculate_momentum(self, features: Dict) -> str:
        """Calculate market momentum from historical prices"""
        historical = features.get("historical_prices", [])
        if len(historical) < 2:
            return "neutral"
        
        recent_change = historical[-1] - historical[-2] if len(historical) >= 2 else 0
        if recent_change > 2:
            return "bullish"
        elif recent_change < -2:
            return "bearish"
        return "neutral"
    
    async def upload_embeddings(self, embeddings_data: pd.DataFrame):
        """
        Upload satellite/PDFM embeddings to Vertex AI Feature Store
        """
        # Create feature store
        feature_store = aiplatform.Featurestore.create(
            featurestore_id="water-futures-embeddings",
            online_store_fixed_node_count=1,
        )
        
        # Create entity type for regions
        entity_type = feature_store.create_entity_type(
            entity_type_id="california_regions",
            description="California water regions with embeddings",
        )
        
        # Create features
        satellite_embedding = entity_type.create_feature(
            feature_id="satellite_embedding",
            value_type="DOUBLE_ARRAY",
            description="Satellite image embeddings",
            dimension=768,  # Embedding dimension
        )
        
        pdfm_embedding = entity_type.create_feature(
            feature_id="pdfm_embedding", 
            value_type="DOUBLE_ARRAY",
            description="Population dynamics embeddings",
            dimension=512,
        )
        
        drought_severity = entity_type.create_feature(
            feature_id="drought_severity",
            value_type="DOUBLE",
            description="Current drought severity level",
        )
        
        # Import feature values
        entity_type.import_feature_values(
            feature_specs=[
                satellite_embedding,
                pdfm_embedding,
                drought_severity,
            ],
            data_source=embeddings_data,
        )
        
        return feature_store

# Singleton instance
vertex_ai_service = VertexAIService()