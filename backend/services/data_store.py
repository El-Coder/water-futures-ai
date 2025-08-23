"""
Simple in-memory data store for hackathon MVP
Replaces database with CSV/JSON file storage
"""
import pandas as pd
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path

class DataStore:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # In-memory caches
        self.water_futures_cache: List[Dict] = []
        self.historical_prices: Optional[pd.DataFrame] = None
        self.embeddings_cache: Dict[str, Any] = {}
        self.news_cache: List[Dict] = []
        self.signals_cache: List[Dict] = []
        
        # Load any existing data
        self.load_historical_data()
        self.load_embeddings()
    
    def load_historical_data(self):
        """Load historical water futures data from CSV"""
        csv_path = self.data_dir / "water_futures_historical.csv"
        if csv_path.exists():
            self.historical_prices = pd.read_csv(csv_path)
            print(f"Loaded {len(self.historical_prices)} historical records")
    
    def upload_csv(self, file_path: str, data_type: str = "historical"):
        """Upload and process CSV file"""
        df = pd.read_csv(file_path)
        
        if data_type == "historical":
            self.historical_prices = df
            # Save to data directory
            df.to_csv(self.data_dir / "water_futures_historical.csv", index=False)
            return {"message": f"Uploaded {len(df)} historical records"}
        
        return {"message": "Data uploaded successfully"}
    
    def load_embeddings(self):
        """Load pre-processed embeddings from JSON"""
        embeddings_path = self.data_dir / "embeddings.json"
        if embeddings_path.exists():
            with open(embeddings_path, 'r') as f:
                self.embeddings_cache = json.load(f)
    
    def get_historical_prices(self, contract_code: str = None, 
                            start_date: str = None, 
                            end_date: str = None) -> pd.DataFrame:
        """Get historical prices with optional filtering"""
        if self.historical_prices is None:
            return pd.DataFrame()
        
        df = self.historical_prices.copy()
        
        if contract_code:
            df = df[df['contract_code'] == contract_code] if 'contract_code' in df.columns else df
        
        if start_date and 'date' in df.columns:
            df = df[pd.to_datetime(df['date']) >= pd.to_datetime(start_date)]
        
        if end_date and 'date' in df.columns:
            df = df[pd.to_datetime(df['date']) <= pd.to_datetime(end_date)]
        
        return df
    
    def add_water_future(self, data: Dict):
        """Add current water future price to cache"""
        data['timestamp'] = datetime.now().isoformat()
        self.water_futures_cache.append(data)
        
        # Keep only last 100 entries in memory
        if len(self.water_futures_cache) > 100:
            self.water_futures_cache = self.water_futures_cache[-100:]
    
    def get_current_prices(self) -> List[Dict]:
        """Get current cached prices"""
        return self.water_futures_cache[-10:] if self.water_futures_cache else []
    
    def add_news_article(self, article: Dict):
        """Add news article to cache"""
        self.news_cache.append(article)
        
        # Keep only last 50 articles
        if len(self.news_cache) > 50:
            self.news_cache = self.news_cache[-50:]
    
    def get_news(self, limit: int = 20) -> List[Dict]:
        """Get cached news articles"""
        return self.news_cache[-limit:]
    
    def add_trading_signal(self, signal: Dict):
        """Add trading signal to cache"""
        signal['generated_at'] = datetime.now().isoformat()
        self.signals_cache.append(signal)
        
        # Keep only last 20 signals
        if len(self.signals_cache) > 20:
            self.signals_cache = self.signals_cache[-20:]
    
    def get_signals(self) -> List[Dict]:
        """Get active trading signals"""
        return [s for s in self.signals_cache if s.get('is_active', True)]
    
    def save_state(self):
        """Save current state to files (optional for persistence)"""
        # Save current prices
        if self.water_futures_cache:
            with open(self.data_dir / "current_prices.json", 'w') as f:
                json.dump(self.water_futures_cache, f)
        
        # Save news cache
        if self.news_cache:
            with open(self.data_dir / "news_cache.json", 'w') as f:
                json.dump(self.news_cache, f)

# Global data store instance
data_store = DataStore()