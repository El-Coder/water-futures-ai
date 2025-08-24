from typing import Optional
from services.trading_service import TradingService
from services.alpaca_service import AlpacaService

class TradingController:
    def __init__(self):
        self.trading_service = TradingService()
        self.alpaca_service = AlpacaService()
    
    async def place_order(
        self,
        contract_code: str,
        side: str,
        quantity: int,
        order_type: str,
        limit_price: Optional[float],
        stop_price: Optional[float]
    ):
        order = await self.alpaca_service.place_order(
            symbol=contract_code,
            side=side,
            quantity=quantity,
            order_type=order_type,
            limit_price=limit_price,
            stop_price=stop_price
        )
        
        await self.trading_service.record_order(order)
        
        return {
            "order_id": order["id"],
            "status": order["status"],
            "message": f"Order placed successfully"
        }
    
    async def get_account(self):
        return await self.alpaca_service.get_account()
    
    async def get_portfolio_status(self):
        portfolio = await self.alpaca_service.get_account()
        positions = await self.alpaca_service.get_positions()
        
        return {
            "total_value": portfolio["portfolio_value"],
            "cash_balance": portfolio["cash"],
            "buying_power": portfolio["buying_power"],
            "positions": positions,
            "daily_pnl": portfolio["daily_pnl"],
            "total_pnl": portfolio["total_pnl"]
        }
    
    async def get_open_positions(self):
        try:
            positions = await self.alpaca_service.get_positions()
            # Ensure we always return an array, even if API fails
            return positions if isinstance(positions, list) else []
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    async def get_orders(self, status: Optional[str]):
        return await self.alpaca_service.get_orders(status)
    
    async def cancel_order(self, order_id: str):
        result = await self.alpaca_service.cancel_order(order_id)
        return {"status": "cancelled", "order_id": order_id}
    
    async def activate_trading_strategy(self, strategy_name: str):
        return await self.trading_service.activate_strategy(strategy_name)
    
    async def deactivate_trading_strategy(self, strategy_name: str):
        return await self.trading_service.deactivate_strategy(strategy_name)