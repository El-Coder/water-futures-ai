"""
Trading Service - Handles trading operations and strategy management
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class TradingService:
    """Service for managing trading operations and strategies"""
    
    def __init__(self):
        self.active_strategies = {}
        self.order_history = []
        self.strategy_configs = {
            "conservative": {
                "max_position": 5,
                "stop_loss": 0.02,
                "take_profit": 0.05
            },
            "moderate": {
                "max_position": 10,
                "stop_loss": 0.03,
                "take_profit": 0.08
            },
            "aggressive": {
                "max_position": 20,
                "stop_loss": 0.05,
                "take_profit": 0.15
            }
        }
    
    async def record_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a trading order in the history
        """
        order_record = {
            "id": order.get("id", f"ORD-{datetime.now().timestamp():.0f}"),
            "timestamp": datetime.now().isoformat(),
            "order_details": order,
            "recorded": True
        }
        
        self.order_history.append(order_record)
        
        # In production, save to database
        # await self._save_to_database(order_record)
        
        return {
            "success": True,
            "order_id": order_record["id"],
            "message": "Order recorded successfully",
            "timestamp": order_record["timestamp"]
        }
    
    async def activate_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """
        Activate a trading strategy
        """
        if strategy_name not in self.strategy_configs:
            return {
                "success": False,
                "error": f"Strategy '{strategy_name}' not found",
                "available_strategies": list(self.strategy_configs.keys())
            }
        
        # Check if already active
        if strategy_name in self.active_strategies:
            return {
                "success": False,
                "error": f"Strategy '{strategy_name}' is already active",
                "status": "already_active"
            }
        
        # Activate the strategy
        strategy_instance = {
            "name": strategy_name,
            "config": self.strategy_configs[strategy_name],
            "activated_at": datetime.now().isoformat(),
            "status": "active",
            "positions": [],
            "pnl": 0.0
        }
        
        self.active_strategies[strategy_name] = strategy_instance
        
        return {
            "success": True,
            "strategy": strategy_name,
            "status": "activated",
            "config": self.strategy_configs[strategy_name],
            "message": f"Strategy '{strategy_name}' activated successfully"
        }
    
    async def deactivate_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """
        Deactivate a trading strategy
        """
        if strategy_name not in self.active_strategies:
            return {
                "success": False,
                "error": f"Strategy '{strategy_name}' is not active",
                "status": "not_active"
            }
        
        # Get strategy details before deactivating
        strategy = self.active_strategies[strategy_name]
        
        # Close any open positions (in production)
        if strategy.get("positions"):
            # await self._close_positions(strategy["positions"])
            positions_closed = len(strategy["positions"])
        else:
            positions_closed = 0
        
        # Remove from active strategies
        del self.active_strategies[strategy_name]
        
        return {
            "success": True,
            "strategy": strategy_name,
            "status": "deactivated",
            "positions_closed": positions_closed,
            "final_pnl": strategy.get("pnl", 0),
            "message": f"Strategy '{strategy_name}' deactivated successfully"
        }
    
    async def get_active_strategies(self) -> List[Dict[str, Any]]:
        """
        Get list of all active strategies
        """
        return [
            {
                "name": name,
                "status": strategy["status"],
                "activated_at": strategy["activated_at"],
                "positions": len(strategy.get("positions", [])),
                "pnl": strategy.get("pnl", 0)
            }
            for name, strategy in self.active_strategies.items()
        ]
    
    async def get_order_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get trading order history
        """
        # Return most recent orders
        return self.order_history[-limit:] if self.order_history else []
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze trading performance
        """
        total_orders = len(self.order_history)
        
        if not self.order_history:
            return {
                "total_orders": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "average_pnl": 0,
                "best_trade": None,
                "worst_trade": None
            }
        
        # Calculate metrics (simplified for demo)
        wins = sum(1 for order in self.order_history 
                  if order.get("order_details", {}).get("pnl", 0) > 0)
        
        total_pnl = sum(order.get("order_details", {}).get("pnl", 0) 
                       for order in self.order_history)
        
        return {
            "total_orders": total_orders,
            "win_rate": (wins / total_orders * 100) if total_orders > 0 else 0,
            "total_pnl": total_pnl,
            "average_pnl": total_pnl / total_orders if total_orders > 0 else 0,
            "active_strategies": len(self.active_strategies),
            "strategies": list(self.active_strategies.keys())
        }
    
    async def get_strategy_recommendations(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get strategy recommendations based on market conditions
        """
        drought_severity = market_conditions.get("drought_severity", 3)
        volatility = market_conditions.get("volatility", "medium")
        
        # Simple recommendation logic
        if drought_severity >= 4:
            recommended = "aggressive"
            reason = "High drought severity suggests potential price increases"
        elif drought_severity <= 2:
            recommended = "conservative"
            reason = "Low drought severity suggests stable prices"
        else:
            recommended = "moderate"
            reason = "Moderate conditions suggest balanced approach"
        
        return {
            "recommended_strategy": recommended,
            "reason": reason,
            "market_conditions": market_conditions,
            "confidence": 0.75,
            "alternative_strategies": [
                s for s in self.strategy_configs.keys() 
                if s != recommended
            ]
        }

# Singleton instance
trading_service = TradingService()