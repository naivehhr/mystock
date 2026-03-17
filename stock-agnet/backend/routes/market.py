"""
行情数据路由
"""
from fastapi import APIRouter, HTTPException
from models import MarketIndex, StockQuote
from data_providers.hybrid_provider import data_provider

router = APIRouter()

@router.get("/index", response_model=MarketIndex)
async def get_market_index(code: str = "1.000001"):
    """
    获取大盘指数
    - code: 指数代码 (1.000001=上证指数, 0.399001=深证成指)
    """
    try:
        return await data_provider.get_market_index(code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(symbol: str):
    """
    获取个股行情
    - symbol: 股票代码 (如 600519)
    """
    try:
        quote = await data_provider.get_stock_quote(symbol)
        if not quote:
            raise HTTPException(status_code=404, detail="股票未找到")
        return quote
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
