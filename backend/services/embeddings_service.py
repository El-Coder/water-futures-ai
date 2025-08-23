"""
Embeddings Service - Handles vector embeddings and similarity search
"""
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

class EmbeddingsService:
    """Service for managing embeddings and vector search"""
    
    def __init__(self):
        self.embeddings_cache = {}
        self.drought_data = self._initialize_drought_data()
        
    def _initialize_drought_data(self) -> List[Dict[str, Any]]:
        """Initialize drought severity data for California regions"""
        return [
            {"name": "Central Valley", "lat": 36.7468, "lng": -119.7726, "severity": 4, "area": "large"},
            {"name": "Imperial Valley", "lat": 32.8475, "lng": -115.5694, "severity": 5, "area": "medium"},
            {"name": "Sacramento Valley", "lat": 39.3633, "lng": -121.9686, "severity": 3, "area": "large"},
            {"name": "San Joaquin Valley", "lat": 36.6062, "lng": -120.1890, "severity": 4, "area": "large"},
            {"name": "Coastal", "lat": 34.0522, "lng": -118.2437, "severity": 2, "area": "medium"},
            {"name": "Salinas Valley", "lat": 36.6777, "lng": -121.6555, "severity": 3, "area": "small"},
            {"name": "Coachella Valley", "lat": 33.6803, "lng": -116.1739, "severity": 5, "area": "small"}
        ]
    
    async def get_drought_map(self) -> Dict[str, Any]:
        """
        Get drought severity map data
        """
        return {
            "regions": self.drought_data,
            "updated_at": datetime.now().isoformat(),
            "summary": {
                "average_severity": np.mean([r["severity"] for r in self.drought_data]),
                "most_affected": max(self.drought_data, key=lambda x: x["severity"])["name"],
                "least_affected": min(self.drought_data, key=lambda x: x["severity"])["name"],
                "total_regions": len(self.drought_data)
            }
        }
    
    async def create_embedding(self, text: str) -> List[float]:
        """
        Create text embedding (mock implementation)
        """
        # In production, would use OpenAI or Vertex AI embeddings
        # For now, return mock embedding
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.randn(384).tolist()
        
        # Cache the embedding
        self.embeddings_cache[text] = embedding
        
        return embedding
    
    async def similarity_search(
        self, 
        query: str, 
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find most similar documents to query
        """
        # Get query embedding
        query_embedding = await self.create_embedding(query)
        query_vec = np.array(query_embedding)
        
        # Calculate similarities
        similarities = []
        for doc in documents:
            doc_embedding = await self.create_embedding(doc)
            doc_vec = np.array(doc_embedding)
            
            # Cosine similarity
            similarity = np.dot(query_vec, doc_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
            )
            
            similarities.append({
                "document": doc,
                "similarity": float(similarity),
                "relevance": "high" if similarity > 0.7 else "medium" if similarity > 0.4 else "low"
            })
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]
    
    async def get_regional_analysis(self, region_name: str) -> Dict[str, Any]:
        """
        Get detailed analysis for a specific region
        """
        region = next((r for r in self.drought_data if r["name"] == region_name), None)
        
        if not region:
            return {"error": f"Region {region_name} not found"}
        
        return {
            "region": region_name,
            "current_severity": region["severity"],
            "severity_level": self._get_severity_level(region["severity"]),
            "coordinates": {"lat": region["lat"], "lng": region["lng"]},
            "area_size": region["area"],
            "recommendations": self._get_regional_recommendations(region["severity"]),
            "water_futures_impact": self._get_market_impact(region["severity"]),
            "subsidy_eligibility": region["severity"] >= 3
        }
    
    def _get_severity_level(self, severity: int) -> str:
        """Convert numeric severity to descriptive level"""
        levels = {
            1: "Minimal",
            2: "Mild",
            3: "Moderate",
            4: "Severe",
            5: "Extreme"
        }
        return levels.get(severity, "Unknown")
    
    def _get_regional_recommendations(self, severity: int) -> List[str]:
        """Get recommendations based on drought severity"""
        if severity >= 4:
            return [
                "Immediately apply for drought relief subsidies",
                "Increase water futures hedge position",
                "Consider switching to drought-resistant crops",
                "Implement emergency water conservation measures"
            ]
        elif severity >= 3:
            return [
                "Monitor water usage closely",
                "Consider water futures for risk management",
                "Evaluate irrigation efficiency",
                "Prepare subsidy application documents"
            ]
        else:
            return [
                "Maintain normal operations",
                "Monitor drought forecasts",
                "Consider preventive measures"
            ]
    
    def _get_market_impact(self, severity: int) -> str:
        """Assess market impact based on drought severity"""
        if severity >= 4:
            return "High - Expect significant price increases in water futures"
        elif severity >= 3:
            return "Moderate - Some upward pressure on water futures prices"
        else:
            return "Low - Minimal impact on water futures prices"
    
    async def get_correlation_analysis(self) -> Dict[str, Any]:
        """
        Analyze correlations between drought severity and market factors
        """
        severities = [r["severity"] for r in self.drought_data]
        
        # Mock correlation data
        return {
            "drought_price_correlation": 0.75,
            "drought_volume_correlation": 0.62,
            "regional_correlations": {
                "central_valley": 0.82,
                "imperial_valley": 0.78,
                "coastal": 0.45
            },
            "confidence": 0.85,
            "sample_period": "2024 YTD",
            "key_insight": "Strong positive correlation between drought severity and water futures prices"
        }

# Singleton instance
embeddings_service = EmbeddingsService()