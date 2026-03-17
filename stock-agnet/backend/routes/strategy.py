"""
策略路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class StrategyRequest(BaseModel):
    symbol: str
    currentPrice: float
    avgCost: float
    action: str
    confidence: float

class StrategyResponse(BaseModel):
    type: str
    takeProfitPrice: Optional[float] = None
    takeProfitRate: Optional[float] = None
    stopLossPrice: Optional[float] = None
    stopLossRate: Optional[float] = None
    conditions: Optional[List[str]] = None

@router.post("/apply", response_model=StrategyResponse)
async def apply_strategy(request: StrategyRequest):
    """
    应用止盈止损策略
    """
    try:
        # 根据操作建议生成止盈止损策略
        if request.action == "卖出":
            stop_loss_rate = 3
            take_profit_rate = 0
        elif request.action == "买入":
            stop_loss_rate = 5
            take_profit_rate = 10
        else:  # 持有
            stop_loss_rate = 8
            take_profit_rate = 15
        
        stop_loss_price = round(request.currentPrice * (1 - stop_loss_rate / 100), 2)
        take_profit_price = round(request.currentPrice * (1 + take_profit_rate / 100), 2) if take_profit_rate > 0 else None
        
        return StrategyResponse(
            type="fixed",
            stopLossPrice=stop_loss_price,
            stopLossRate=stop_loss_rate,
            takeProfitPrice=take_profit_price,
            takeProfitRate=take_profit_rate if take_profit_rate > 0 else None,
            conditions=[
                f"当价格低于 {stop_loss_price} 时触发止损",
                f"当价格高于 {take_profit_price} 时触发止盈" if take_profit_price else "暂不止盈"
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
