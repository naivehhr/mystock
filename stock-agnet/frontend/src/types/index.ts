// 持仓数据
export interface Position {
  symbol: string
  name: string
  quantity: number
  avgCost: number
  currentPrice: number
  marketValue: number
  profitLoss: number
  profitRate: number
}

// 投资组合
export interface Portfolio {
  positions: Position[]
  totalMarketValue: number
  totalProfitLoss: number
  totalProfitRate: number
}

// 大盘指数
export interface MarketIndex {
  name: string
  code: string
  current: number
  change: number
  changeRate: number
}

// 个股行情
export interface StockQuote {
  symbol: string
  name: string
  current: number
  open: number
  high: number
  low: number
  volume: number
  amount: number
  change: number
  changeRate: number
}

// 技术指标
export interface TechnicalIndicators {
  ma5: number
  ma10: number
  ma20: number
  ma60: number
  macd: {
    diff: number
    dea: number
    histogram: number
  }
  kdj: {
    k: number
    d: number
    j: number
  }
}

// 资金流向
export interface CapitalFlow {
  mainInflow: number
  mainInflowRate: number
  retailInflow: number
  retailInflowRate: number
}

// 多维度分析
export interface Analysis {
  symbol: string
  name: string
  technical: TechnicalIndicators
  capital: CapitalFlow
  news: string[]
}

// 止盈止损策略
export interface StopStrategy {
  type: 'fixed' | 'trailing' | 'conditional'
  takeProfitPrice?: number
  takeProfitRate?: number
  stopLossPrice?: number
  stopLossRate?: number
  conditions?: string[]
}

// 操作建议
export interface Recommendation {
  action: '买入' | '卖出' | '持有'
  reason: string
  confidence: number
}

// 个股分析结果
export interface StockAnalysis {
  position: Position
  quote: StockQuote
  analysis: Analysis
  strategy: StopStrategy
  recommendation: Recommendation
}

// 总体分析结果
export interface AnalysisResult {
  portfolio: Portfolio
  marketIndex: MarketIndex
  stockAnalyses: StockAnalysis[]
  overallRecommendation: Recommendation
}
