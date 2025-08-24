"""
Water Futures Service - Handles water futures contract operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from services.data_store import data_store

class WaterFuturesService:
    """Service for managing water futures contracts and data"""
    
    def __init__(self):
        self.contracts = {
            "NQH25": {
                "name": "March 2025 Water Futures",
                "expiry": "2025-03-31",
                "current_price": 508.00,
                "volume": 125000,
                "open_interest": 50000,
                "contract_size": 100,
                "tick_size": 0.25
            },
            "NQM25": {
                "name": "June 2025 Water Futures",
                "expiry": "2025-06-30",
                "current_price": 512.50,
                "volume": 98000,
                "open_interest": 42000,
                "contract_size": 100,
                "tick_size": 0.25
            },
            "NQU25": {
                "name": "September 2025 Water Futures",
                "expiry": "2025-09-30",
                "current_price": 515.75,
                "volume": 75000,
                "open_interest": 35000,
                "contract_size": 100,
                "tick_size": 0.25
            },
            "NQZ25": {
                "name": "December 2025 Water Futures",
                "expiry": "2025-12-31",
                "current_price": 520.00,
                "volume": 60000,
                "open_interest": 28000,
                "contract_size": 100,
                "tick_size": 0.25
            }
        }
    
    async def get_contracts(self) -> List[Dict[str, Any]]:
        """
        Get all available water futures contracts
        """
        return [
            {
                "contract_code": code,
                **details,
                "last_updated": datetime.now().isoformat()
            }
            for code, details in self.contracts.items()
        ]
    
    async def get_contract(self, contract_code: str) -> Dict[str, Any]:
        """
        Get details for a specific contract
        """
        if contract_code not in self.contracts:
            raise ValueError(f"Contract {contract_code} not found")
        
        contract = self.contracts[contract_code].copy()
        contract["contract_code"] = contract_code
        
        # Add calculated fields
        contract["days_to_expiry"] = (
            datetime.strptime(contract["expiry"], "%Y-%m-%d") - datetime.now()
        ).days
        
        # Get historical data if available
        historical_data = data_store.get_historical_prices(contract_code)
        if not historical_data.empty and 'close' in historical_data.columns:
            contract["52_week_high"] = historical_data['close'].max()
            contract["52_week_low"] = historical_data['close'].min()
            contract["avg_volume_30d"] = historical_data.tail(30)['volume'].mean() if 'volume' in historical_data.columns else 0
        
        return contract
    
    async def get_current_prices(self) -> List[Dict[str, Any]]:
        """
        Get current prices for all contracts
        """
        try:
            prices = []
            for code, details in self.contracts.items():
                prices.append({
                    "contract_code": code,
                    "name": details["name"],
                    "price": details["current_price"],
                    "change": 2.50,  # Mock data
                    "change_percent": 0.49,  # Mock data
                    "volume": details["volume"],
                    "timestamp": datetime.now().isoformat()
                })
            return prices
        except Exception as e:
            print(f"Error fetching current prices: {e}")
            return []
    
    async def get_historical_prices(
        self, 
        contract_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical price data
        """
        # Ensure parameters are not None
        safe_contract_code = contract_code or "NQH25"
        safe_start_date = start_date or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        safe_end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        
        df = data_store.get_historical_prices(safe_contract_code, safe_start_date, safe_end_date)
        
        if df.empty:
            # Return mock data if no historical data available
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now(),
                freq='D'
            )
            
            mock_data = []
            base_price = 500.0
            for i, date in enumerate(dates):
                price = base_price + (i * 0.5) + (i % 3 - 1) * 2  # Simple pattern
                mock_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "contract_code": contract_code or "NQH25",
                    "open": price - 1,
                    "high": price + 2,
                    "low": price - 2,
                    "close": price,
                    "volume": 100000 + (i * 1000)
                })
            return mock_data
        
        return df.to_dict(orient="records")
    
    async def update_price(self, contract_code: str, new_price: float) -> Dict[str, Any]:
        """
        Update the current price of a contract
        """
        if contract_code not in self.contracts:
            raise ValueError(f"Contract {contract_code} not found")
        
        old_price = self.contracts[contract_code]["current_price"]
        self.contracts[contract_code]["current_price"] = new_price
        
        return {
            "contract_code": contract_code,
            "old_price": old_price,
            "new_price": new_price,
            "change": new_price - old_price,
            "change_percent": ((new_price - old_price) / old_price) * 100,
            "updated_at": datetime.now().isoformat()
        }
    
    async def calculate_margin_requirement(
        self, 
        contract_code: str, 
        quantity: int
    ) -> Dict[str, Any]:
        """
        Calculate margin requirements for a position
        """
        if contract_code not in self.contracts:
            raise ValueError(f"Contract {contract_code} not found")
        
        contract = self.contracts[contract_code]
        contract_value = contract["current_price"] * contract["contract_size"] * quantity
        
        # Typical margin requirements
        initial_margin = contract_value * 0.10  # 10% initial margin
        maintenance_margin = contract_value * 0.075  # 7.5% maintenance margin
        
        return {
            "contract_code": contract_code,
            "quantity": quantity,
            "contract_value": contract_value,
            "initial_margin": initial_margin,
            "maintenance_margin": maintenance_margin,
            "margin_call_price": contract["current_price"] * 0.925  # 7.5% below current
        }
    
    async def get_market_depth(self, contract_code: str) -> Dict[str, Any]:
        """
        Get market depth (order book) for a contract
        """
        if contract_code not in self.contracts:
            raise ValueError(f"Contract {contract_code} not found")
        
        current_price = self.contracts[contract_code]["current_price"]
        
        # Generate mock order book
        bids = []
        asks = []
        
        for i in range(5):
            bid_price = current_price - (i + 1) * 0.25
            ask_price = current_price + (i + 1) * 0.25
            
            bids.append({
                "price": bid_price,
                "quantity": 100 - (i * 15),
                "orders": 5 - i
            })
            
            asks.append({
                "price": ask_price,
                "quantity": 100 - (i * 15),
                "orders": 5 - i
            })
        
        return {
            "contract_code": contract_code,
            "bids": bids,
            "asks": asks,
            "spread": asks[0]["price"] - bids[0]["price"],
            "mid_price": (asks[0]["price"] + bids[0]["price"]) / 2,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_contract_specifications(self, contract_code: str) -> Dict[str, Any]:
        """
        Get detailed specifications for a contract
        """
        if contract_code not in self.contracts:
            raise ValueError(f"Contract {contract_code} not found")
        
        contract = self.contracts[contract_code]
        
        return {
            "contract_code": contract_code,
            "name": contract["name"],
            "underlying": "California Water Index",
            "contract_size": contract["contract_size"],
            "contract_unit": "acre-feet",
            "price_quotation": "USD per acre-foot",
            "tick_size": contract["tick_size"],
            "tick_value": contract["tick_size"] * contract["contract_size"],
            "expiry_date": contract["expiry"],
            "settlement": "Cash",
            "trading_hours": "6:00 AM - 5:00 PM PT",
            "exchange": "CME Group (Simulated)",
            "initial_margin": "10%",
            "maintenance_margin": "7.5%"
        }

    async def get_nasdaq_water_index(self) -> Dict[str, Any]:
        """
        Get current NQH2O water index data
        """
        return {
            "index_code": "NQH2O",
            "name": "NASDAQ Veles California Water Index",
            "current_value": 508.25,
            "change": 2.50,
            "change_percent": 0.49,
            "volume": 125000,
            "high_52_week": 525.00,
            "low_52_week": 485.00,
            "last_updated": datetime.now().isoformat(),
            "source": "NASDAQ"
        }

    async def get_historical_data(
        self, 
        contract_code: str, 
        start_date: str = None, 
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Get historical price data for a contract
        """
        if contract_code not in self.contracts:
            raise ValueError(f"Contract {contract_code} not found")
        
        # Get data from data store
        historical_data = data_store.get_historical_prices(contract_code)
        
        if historical_data.empty:
            # Return mock data if no historical data available
            return {
                "contract_code": contract_code,
                "data": [],
                "message": "No historical data available",
                "start_date": start_date,
                "end_date": end_date
            }
        
        # Filter by date range if provided
        if start_date and not historical_data.empty:
            historical_data = historical_data[historical_data.index >= start_date]
        if end_date and not historical_data.empty:
            historical_data = historical_data[historical_data.index <= end_date]
        
        # Convert to list format
        data_list = []
        if not historical_data.empty:
            for date, row in historical_data.iterrows():
                try:
                    data_list.append({
                        "date": str(date) if hasattr(date, 'strftime') else str(date),
                        "open": float(row.get('open', 0) or 0),
                        "high": float(row.get('high', 0) or 0),
                        "low": float(row.get('low', 0) or 0),
                        "close": float(row.get('close', 0) or 0),
                        "volume": int(row.get('volume', 0) or 0)
                    })
                except (ValueError, TypeError):
                    # Skip rows with invalid data
                    continue
        
        return {
            "contract_code": contract_code,
            "data": data_list,
            "start_date": start_date,
            "end_date": end_date,
            "total_records": len(data_list)
        }

    async def get_available_contracts(self) -> List[Dict[str, Any]]:
        """
        Get list of all available contracts
        """
        return await self.get_contracts()

    async def refresh_all_market_data(self) -> Dict[str, Any]:
        """
        Refresh all market data from external sources
        """
        # In production, this would fetch from real data sources
        updated_contracts = []
        
        for code, contract in self.contracts.items():
            # Simulate price updates
            price_change = (datetime.now().second % 10 - 5) * 0.25  # Random change
            new_price = contract["current_price"] + price_change
            
            self.contracts[code]["current_price"] = new_price
            self.contracts[code]["volume"] += (datetime.now().second % 1000)
            
            updated_contracts.append({
                "contract_code": code,
                "old_price": contract["current_price"],
                "new_price": new_price,
                "change": price_change
            })
        
        return {
            "status": "success",
            "updated_contracts": updated_contracts,
            "total_updated": len(updated_contracts),
            "refresh_time": datetime.now().isoformat()
        }

# Singleton instance
water_futures_service = WaterFuturesService()