from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from api.controllers.trading_controller import TradingController
from pydantic import BaseModel

router = APIRouter()
controller = TradingController()

class OrderRequest(BaseModel):
    contract_code: str
    side: str  # BUY or SELL
    quantity: int
    order_type: str = "market"
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str

@router.post("/order", response_model=OrderResponse)
async def place_order(request: OrderRequest):
    try:
        return await controller.place_order(
            contract_code=request.contract_code,
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            limit_price=request.limit_price,
            stop_price=request.stop_price
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/account")
async def get_account():
    try:
        return await controller.get_account()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio")
async def get_portfolio():
    try:
        return await controller.get_portfolio_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_positions():
    try:
        return await controller.get_open_positions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders")
async def get_orders(status: Optional[str] = None):
    """Get all orders from Alpaca, including accepted but not filled"""
    try:
        # If no status specified, get all open orders (accepted, new, partially_filled)
        if not status:
            # Get all non-closed orders
            orders = await controller.get_orders(None)
            # Return all orders that aren't closed
            return [o for o in orders if o.get('status') not in ['filled', 'cancelled', 'expired']]
        else:
            return await controller.get_orders(status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/all")
async def get_all_orders():
    """Get ALL orders including filled and cancelled"""
    try:
        return await controller.get_orders(None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    try:
        return await controller.cancel_order(order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategy/{strategy_name}/activate")
async def activate_strategy(strategy_name: str):
    try:
        return await controller.activate_trading_strategy(strategy_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategy/{strategy_name}/deactivate")
async def deactivate_strategy(strategy_name: str):
    try:
        return await controller.deactivate_trading_strategy(strategy_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))