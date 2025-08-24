"""
Alpaca MCP Client - Connects to Alpaca MCP Server for trading
"""
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AlpacaMCPClient:
    def __init__(self):
        # Alpaca credentials from environment variables only
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.api_secret = os.getenv("ALPACA_SECRET_KEY")
        
        # Initialize Alpaca client for direct trading (only if credentials exist)
        if self.api_key and self.api_secret:
            self.trading_client = TradingClient(
                api_key=self.api_key,
                secret_key=self.api_secret,
                paper=True  # Use paper trading for testing
            )
        else:
            self.trading_client = None
            print("⚠️  Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables.")
        
        # MCP server endpoint (if running)
        self.mcp_server_url = os.getenv("ALPACA_MCP_URL", "http://localhost:8765")
    
    async def place_water_futures_order(
        self, 
        symbol: str, 
        quantity: int, 
        side: str,
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """
        Place a water futures order through Alpaca
        For demo, we'll use SPY as a proxy for water futures
        """
        try:
            # Map water futures symbols to tradeable securities
            # In production, would use actual water futures contracts
            symbol_mapping = {
                "NQH25": "SPY",  # Using SPY as proxy for demo
                "NQM25": "QQQ",  # Using QQQ as proxy
                "WATER": "AWK",  # American Water Works as proxy
            }
            
            trade_symbol = symbol_mapping.get(symbol, "SPY")
            
            # Create order request
            order_data = MarketOrderRequest(
                symbol=trade_symbol,
                qty=quantity,
                side=OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = self.trading_client.submit_order(order_data)
            
            return {
                "success": True,
                "order_id": getattr(order, 'id', f"ORDER-{symbol}-{quantity}"),
                "symbol": symbol,
                "traded_symbol": trade_symbol,
                "quantity": quantity,
                "side": side,
                "status": getattr(order, 'status', 'submitted'),
                "submitted_at": str(getattr(order, 'submitted_at', datetime.now())),
                "message": f"Order placed successfully for {quantity} shares of {trade_symbol} (proxy for {symbol})"
            }
            
        except Exception as e:
            print(f"Alpaca order error: {e}")
            # Return error instead of simulated success
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to place order with Alpaca"
            }
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get Alpaca account information
        """
        try:
            account = self.trading_client.get_account()
            
            return {
                "buying_power": float(getattr(account, 'buying_power', 100000.0)),
                "cash": float(getattr(account, 'cash', 95000.0)),
                "portfolio_value": float(getattr(account, 'portfolio_value', 125000.0)),
                "day_trade_count": getattr(account, 'daytrade_count', 0),
                "pattern_day_trader": getattr(account, 'pattern_day_trader', False),
                "trading_blocked": getattr(account, 'trading_blocked', False),
                "account_blocked": getattr(account, 'account_blocked', False),
                "status": getattr(account, 'status', 'ACTIVE')
            }
        except Exception as e:
            print(f"Account info error: {e}")
            # Return zeros instead of dummy data
            return {
                "buying_power": 0.00,
                "cash": 0.00,
                "portfolio_value": 0.00,
                "status": "ERROR",
                "error": str(e)
            }
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions
        """
        try:
            positions = self.trading_client.get_all_positions()
            
            return [
                {
                    "symbol": getattr(pos, 'symbol', 'UNKNOWN'),
                    "qty": float(getattr(pos, 'qty', 0)),
                    "avg_entry_price": float(getattr(pos, 'avg_entry_price', 0)),
                    "market_value": float(getattr(pos, 'market_value', 0)),
                    "unrealized_pl": float(getattr(pos, 'unrealized_pl', 0)),
                    "unrealized_plpc": float(getattr(pos, 'unrealized_plpc', 0)),
                    "side": getattr(pos, 'side', 'long')
                }
                for pos in positions
            ]
        except Exception as e:
            print(f"Positions error: {e}")
            # Return empty array instead of dummy positions
            return []
    
    async def get_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get orders from Alpaca
        """
        try:
            if self.trading_client:
                from alpaca.trading.requests import GetOrdersRequest
                from alpaca.trading.enums import QueryOrderStatus
                
                # Create request with optional status filter
                request = GetOrdersRequest(status=status) if status else GetOrdersRequest()
                orders = self.trading_client.get_orders(request)
                
                # Format orders for response
                formatted_orders = []
                for order in orders:
                    formatted_orders.append({
                        "id": getattr(order, 'id', ''),
                        "symbol": getattr(order, 'symbol', ''),
                        "qty": getattr(order, 'qty', 0),
                        "side": getattr(order, 'side', ''),
                        "status": getattr(order, 'status', ''),
                        "created_at": str(getattr(order, 'created_at', '')),
                        "filled_qty": getattr(order, 'filled_qty', 0),
                        "filled_avg_price": getattr(order, 'filled_avg_price', None)
                    })
                return formatted_orders
            return []
        except Exception as e:
            print(f"Error getting orders: {e}")
            return []
    
    async def get_market_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a symbol
        """
        try:
            # Map water futures to tradeable symbol
            trade_symbol = {"NQH25": "SPY", "NQM25": "QQQ"}.get(symbol, "SPY")
            
            # TODO: Implement real Alpaca market data API call
            return {
                "symbol": symbol,
                "trade_symbol": trade_symbol,
                "error": "Market data not available"
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e)
            }
    
    async def call_mcp_server(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Alpaca MCP server if running
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_server_url}/rpc",
                    json={
                        "jsonrpc": "2.0",
                        "method": method,
                        "params": params,
                        "id": 1
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json().get("result", {})
                    
        except Exception as e:
            print(f"MCP server call failed: {e}")
        
        # Fallback to direct API call
        if method == "place_stock_order":
            symbol = params.get("symbol")
            quantity = params.get("qty")
            side = params.get("side")
            
            if symbol is None or quantity is None or side is None:
                return {"error": "Missing required parameters"}
                
            return await self.place_water_futures_order(
                symbol=symbol,
                quantity=quantity,
                side=side,
                order_type=params.get("type", "market")
            )
        elif method == "get_account_info":
            return await self.get_account_info()
        elif method == "get_positions":
            return await self.get_positions()
        
        return {"error": "Method not supported", "method": method, "result": None}

# Singleton instance
alpaca_client = AlpacaMCPClient()