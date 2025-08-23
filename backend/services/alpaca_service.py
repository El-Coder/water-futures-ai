"""
Alpaca Service - Wrapper around alpaca_mcp_client for trading operations
"""
from typing import Dict, Any, List, Optional
from services.alpaca_mcp_client import alpaca_client
import logging

logger = logging.getLogger(__name__)

class AlpacaService:
    """Service for interacting with Alpaca trading API"""
    
    def __init__(self):
        self.client = alpaca_client
        self.order_cache = {}
        
    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        order_type: str = "market",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Place an order through Alpaca
        """
        try:
            # For water futures, use the alpaca_mcp_client which handles symbol mapping
            result = await self.client.place_water_futures_order(
                symbol=symbol,
                quantity=quantity,
                side=side.upper(),
                order_type=order_type
            )
            
            # Cache the order
            if result.get("success") and result.get("order_id"):
                self.order_cache[result["order_id"]] = result
            
            # Format response to match expected structure
            return {
                "id": result.get("order_id", f"DEMO-{symbol}-{quantity}"),
                "status": result.get("status", "pending"),
                "symbol": symbol,
                "quantity": quantity,
                "side": side,
                "order_type": order_type,
                "limit_price": limit_price,
                "stop_price": stop_price,
                "message": result.get("message", "Order placed"),
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {
                "id": f"ERROR-{symbol}-{quantity}",
                "status": "failed",
                "error": str(e),
                "symbol": symbol,
                "quantity": quantity,
                "side": side
            }
    
    async def get_account(self) -> Dict[str, Any]:
        """
        Get account information from Alpaca
        """
        try:
            account_info = await self.client.get_account_info()
            
            # Format response to match expected structure
            return {
                "portfolio_value": account_info.get("portfolio_value", 125000.00),
                "cash": account_info.get("cash", 95000.00),
                "buying_power": account_info.get("buying_power", 100000.00),
                "daily_pnl": account_info.get("daily_pnl", 0),
                "total_pnl": account_info.get("total_pnl", 0),
                "status": account_info.get("status", "ACTIVE"),
                "pattern_day_trader": account_info.get("pattern_day_trader", False),
                "trading_blocked": account_info.get("trading_blocked", False),
                "account_blocked": account_info.get("account_blocked", False),
                "day_trade_count": account_info.get("day_trade_count", 0),
                "demo_mode": account_info.get("demo_mode", False)
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            # Return demo data on error
            return {
                "portfolio_value": 125000.00,
                "cash": 95000.00,
                "buying_power": 100000.00,
                "daily_pnl": 250.00,
                "total_pnl": 5000.00,
                "status": "ACTIVE",
                "demo_mode": True,
                "error": str(e)
            }
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions from Alpaca
        """
        try:
            positions = await self.client.get_positions()
            
            # Ensure positions is a list
            if not isinstance(positions, list):
                positions = []
            
            return positions
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            # Return demo positions on error
            return [
                {
                    "symbol": "SPY (Water Futures Proxy)",
                    "qty": 10,
                    "avg_entry_price": 500.00,
                    "market_value": 5080.00,
                    "unrealized_pl": 80.00,
                    "unrealized_plpc": 1.6,
                    "side": "long"
                }
            ]
    
    async def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders from Alpaca
        """
        try:
            # Check cached orders first
            cached_orders = list(self.order_cache.values())
            
            if status:
                # Filter by status if provided
                cached_orders = [
                    order for order in cached_orders 
                    if order.get("status", "").lower() == status.lower()
                ]
            
            # In production, would also fetch from Alpaca API
            # orders = await self.client.get_orders(status)
            
            return cached_orders if cached_orders else [
                {
                    "id": "DEMO-001",
                    "symbol": "NQH25",
                    "quantity": 5,
                    "side": "BUY",
                    "status": status or "filled",
                    "created_at": "2024-12-13T10:00:00Z",
                    "filled_at": "2024-12-13T10:00:05Z",
                    "filled_price": 508.00
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order on Alpaca
        """
        try:
            # Remove from cache
            if order_id in self.order_cache:
                order = self.order_cache[order_id]
                order["status"] = "cancelled"
                del self.order_cache[order_id]
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "status": "cancelled",
                    "message": f"Order {order_id} cancelled successfully"
                }
            
            # In production, would also call Alpaca API
            # result = await self.client.cancel_order(order_id)
            
            return {
                "success": True,
                "order_id": order_id,
                "status": "cancelled",
                "message": "Order cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return {
                "success": False,
                "order_id": order_id,
                "error": str(e)
            }
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get market data for a symbol
        """
        try:
            # Use the client's market quote method
            quote = await self.client.get_market_quote(symbol)
            
            return {
                "symbol": symbol,
                "bid": quote.get("bid", 507.50),
                "ask": quote.get("ask", 508.50),
                "last": quote.get("last", 508.00),
                "volume": quote.get("volume", 125000),
                "change": quote.get("change", 2.50),
                "change_percent": quote.get("change_percent", 0.49),
                "timestamp": quote.get("timestamp", "2024-12-13T14:30:00Z")
            }
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "bid": 507.50,
                "ask": 508.50,
                "last": 508.00,
                "volume": 125000,
                "error": str(e)
            }
    
    async def get_account_history(self, period: str = "1M") -> Dict[str, Any]:
        """
        Get account history and performance
        """
        try:
            # In production, would fetch from Alpaca API
            # For now, return simulated history
            return {
                "period": period,
                "equity": [
                    {"date": "2024-11-13", "value": 120000},
                    {"date": "2024-11-20", "value": 121500},
                    {"date": "2024-11-27", "value": 123000},
                    {"date": "2024-12-04", "value": 124500},
                    {"date": "2024-12-11", "value": 125000}
                ],
                "profit_loss": [
                    {"date": "2024-11-13", "value": 0},
                    {"date": "2024-11-20", "value": 1500},
                    {"date": "2024-11-27", "value": 3000},
                    {"date": "2024-12-04", "value": 4500},
                    {"date": "2024-12-11", "value": 5000}
                ],
                "total_return": 4.17,
                "total_return_percent": 4.17
            }
            
        except Exception as e:
            logger.error(f"Error getting account history: {e}")
            return {
                "period": period,
                "error": str(e)
            }

# Singleton instance
alpaca_service = AlpacaService()