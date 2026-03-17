"""
持仓分析路由
"""
import json
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from models import Portfolio, AnalysisResult, Recommendation
from services.analysis import analysis_engine
import database

router = APIRouter()


class SavePortfolioRequest(BaseModel):
    name: str
    portfolio: Portfolio


class AnalyzeRequest(BaseModel):
    portfolio: Portfolio
    save_to_db: bool = False
    portfolio_name: str = None


# 存储最近一次分析结果（内存中）
_last_analysis_result = None
_last_analysis_time = None


# 支持直接传 Portfolio 或 AnalyzeRequest
@router.post("/analyze", response_model=AnalysisResult)
def analyze_portfolio(portfolio: Portfolio):
    """
    分析持仓组合
    """
    global _last_analysis_result
    try:
        # 获取大盘数据
        market_index = analysis_engine.get_market_index_data()
        
        # 分析每只股票
        stock_analyses = analysis_engine.analyze_portfolio(portfolio)
        
        # 生成总体建议
        overall_recommendation = _generate_overall_recommendation(stock_analyses)
        
        result = AnalysisResult(
            portfolio=portfolio,
            marketIndex=market_index,
            stockAnalyses=stock_analyses,
            overallRecommendation=overall_recommendation
        )
        
        # 保存到内存中作为历史数据
        _last_analysis_result = result
        _last_analysis_time = datetime.now().isoformat()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from datetime import datetime

@router.get("/history")
def get_last_analysis():
    """
    获取最近一次分析结果
    """
    if _last_analysis_result is None:
        raise HTTPException(status_code=404, detail="暂无分析历史")
    return {
        "data": _last_analysis_result,
        "analysisTime": _last_analysis_time
    }


@router.post("/clear")
def clear_analysis_history():
    """
    清空分析历史
    """
    global _last_analysis_result
    _last_analysis_result = None
    return {"success": True, "message": "分析历史已清空"}


@router.post("/save", response_model=dict)
def save_portfolio(request: SavePortfolioRequest):
    """
    保存持仓组合到数据库
    """
    try:
        positions_data = []
        for pos in request.portfolio.positions:
            positions_data.append({
                "symbol": pos.symbol,
                "name": pos.name,
                "quantity": pos.quantity,
                "avgCost": pos.avgCost,
                "currentPrice": pos.currentPrice,
                "marketValue": pos.marketValue,
                "profitLoss": pos.profitLoss,
                "profitRate": pos.profitRate
            })
        
        portfolio_id = database.save_portfolio(request.name, positions_data)
        
        return {
            "success": True,
            "portfolio_id": portfolio_id,
            "message": f"持仓组合 '{request.name}' 已保存"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[dict])
def list_portfolios():
    """
    获取所有持仓组合列表
    """
    try:
        portfolios = database.get_all_portfolios()
        return portfolios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{portfolio_id}", response_model=dict)
def get_portfolio(portfolio_id: int):
    """
    获取指定持仓组合详情
    """
    try:
        portfolio = database.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="持仓组合不存在")
        return portfolio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int):
    """
    删除持仓组合
    """
    try:
        deleted = database.delete_portfolio(portfolio_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="持仓组合不存在")
        return {"success": True, "message": "持仓组合已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{portfolio_id}", response_model=List[dict])
def get_analysis_history(portfolio_id: int, limit: int = 10):
    """
    获取持仓组合的分析历史
    """
    try:
        history = database.get_analysis_history(portfolio_id, limit)
        for h in history:
            h["analysis_data"] = json.loads(h["analysis_data"])
            if h.get("overall_recommendation"):
                h["overall_recommendation"] = json.loads(h["overall_recommendation"])
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_overall_recommendation(stock_analyses) -> Recommendation:
    """生成总体建议"""
    if not stock_analyses:
        return Recommendation(
            action="持有",
            reason="暂无持仓数据",
            confidence=0
        )
    
    buy_count = sum(1 for s in stock_analyses if s.recommendation.action == "买入")
    sell_count = sum(1 for s in stock_analyses if s.recommendation.action == "卖出")
    hold_count = sum(1 for s in stock_analyses if s.recommendation.action == "持有")
    total = len(stock_analyses)
    
    avg_confidence = sum(s.recommendation.confidence for s in stock_analyses) / total
    
    if buy_count > sell_count and buy_count > hold_count:
        action = "买入"
        reason = f"{buy_count}只股票建议买入"
    elif sell_count > buy_count and sell_count > hold_count:
        action = "卖出"
        reason = f"{sell_count}只股票建议卖出"
    else:
        action = "持有"
        reason = f"{hold_count}只股票建议持有"
    
    return Recommendation(
        action=action,
        reason=reason,
        confidence=avg_confidence
    )
