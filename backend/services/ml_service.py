"""
ML Service - Machine Learning service for predictions and analysis
"""
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta
from services.vertex_ai_service import vertex_ai_service

class MLService:
    """Service for machine learning operations"""
    
    def __init__(self):
        self.vertex_ai = vertex_ai_service
        self.model_cache = {}
        
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a prediction using ML models
        """
        # Use Vertex AI for predictions
        return await self.vertex_ai.predict(features)
    
    async def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train or retrain ML model
        """
        # In production, would trigger Vertex AI training job
        return {
            "status": "training_started",
            "job_id": f"JOB-{datetime.now().timestamp():.0f}",
            "estimated_time": "2 hours",
            "message": "Model training initiated"
        }
    
    async def evaluate_model(self, model_name: str) -> Dict[str, Any]:
        """
        Evaluate model performance
        """
        # Mock evaluation metrics
        return {
            "model_name": model_name,
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85,
                "mse": 2.5,
                "mae": 1.8
            },
            "evaluation_date": datetime.now().isoformat(),
            "test_set_size": 1000
        }
    
    async def get_feature_importance(self) -> List[Dict[str, Any]]:
        """
        Get feature importance for the model
        """
        return [
            {"feature": "drought_severity", "importance": 0.35},
            {"feature": "historical_price", "importance": 0.25},
            {"feature": "precipitation", "importance": 0.15},
            {"feature": "temperature", "importance": 0.10},
            {"feature": "season", "importance": 0.08},
            {"feature": "market_volume", "importance": 0.07}
        ]
    
    async def detect_anomalies(self, data: List[float]) -> Dict[str, Any]:
        """
        Detect anomalies in time series data
        """
        if not data:
            return {"anomalies": [], "message": "No data provided"}
        
        # Simple statistical anomaly detection
        mean = np.mean(data)
        std = np.std(data)
        threshold = 2  # 2 standard deviations
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / std) if std > 0 else 0
            if z_score > threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": z_score,
                    "severity": "high" if z_score > 3 else "medium"
                })
        
        return {
            "anomalies": anomalies,
            "total_points": len(data),
            "anomaly_count": len(anomalies),
            "anomaly_rate": len(anomalies) / len(data) if data else 0
        }
    
    async def generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """
        Generate insights from data
        """
        insights = []
        
        # Analyze drought severity
        if "drought_severity" in data:
            severity = data["drought_severity"]
            if severity >= 4:
                insights.append("Severe drought conditions detected - consider increasing hedge positions")
            elif severity <= 2:
                insights.append("Mild drought conditions - market prices may stabilize")
        
        # Analyze price trends
        if "price_trend" in data:
            trend = data["price_trend"]
            if trend > 0.05:
                insights.append("Strong upward price trend detected")
            elif trend < -0.05:
                insights.append("Downward price pressure observed")
        
        # Analyze volume
        if "volume_change" in data:
            change = data["volume_change"]
            if abs(change) > 0.2:
                insights.append(f"Significant volume change: {change*100:.1f}%")
        
        if not insights:
            insights.append("Market conditions appear stable")
        
        return insights

# Singleton instance
ml_service = MLService()