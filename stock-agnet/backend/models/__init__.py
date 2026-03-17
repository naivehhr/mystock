"""
数据模型定义
"""
from pydantic import BaseModel
from typing import List, Optional

# 持仓数据
class Position(BaseModel):
    symbol: str
    name: str
    quantity: int
    avgCost: float
    currentPrice: float
    marketValue: float
    profitLoss: float
    profitRate: float

class Portfolio(BaseModel):
    positions: List[Position]
    totalMarketValue: float
    totalProfitLoss: float
    totalProfitRate: float

# 大盘指数
class MarketIndex(BaseModel):
    name: str
    code: str
    current: float
    change: float
    changeRate: float

# 个股行情
class StockQuote(BaseModel):
    symbol: str
    name: str
    current: float
    open: float
    high: float
    low: float
    volume: float
    amount: float
    change: float
    changeRate: float

# 技术指标
class MACD(BaseModel):
    diff: float
    dea: float
    histogram: float

class KDJ(BaseModel):
    k: float
    d: float
    j: float

class TechnicalIndicators(BaseModel):
    ma5: float
    ma10: float
    ma20: float
    ma60: float
    macd: MACD
    kdj: KDJ

# 资金流向
class CapitalFlow(BaseModel):
    mainInflow: float
    mainInflowRate: float
    retailInflow: float
    retailInflowRate: float

# 多维度分析
class Analysis(BaseModel):
    symbol: str
    name: str
    technical: TechnicalIndicators
    capital: CapitalFlow
    news: List[str]

# 止盈止损策略
class StopStrategy(BaseModel):
    type: str  # 'fixed', 'trailing', 'conditional'
    takeProfitPrice: Optional[float] = None
    takeProfitRate: Optional[float] = None
    stopLossPrice: Optional[float] = None
    stopLossRate: Optional[float] = None
    conditions: Optional[List[str]] = None

# 操作建议
class Recommendation(BaseModel):
    action: str  # '买入', '卖出', '持有'
    reason: str
    confidence: float

# 个股分析结果
class StockAnalysis(BaseModel):
    position: Position
    quote: StockQuote
    analysis: Analysis
    strategy: StopStrategy
    recommendation: Recommendation

# 总体分析结果
class AnalysisResult(BaseModel):
    portfolio: Portfolio
    marketIndex: MarketIndex
    stockAnalyses: List[StockAnalysis]
    overallRecommendation: Recommendation
