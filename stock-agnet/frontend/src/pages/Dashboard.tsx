import { useState } from 'react'
import { AnalysisResult, StockAnalysis } from '../types'
import PortfolioPieChart from '../components/charts/PortfolioPieChart'
import ProfitLossChart from '../components/charts/ProfitLossChart'
import './Dashboard.css'

interface Props {
  data: AnalysisResult
  isEmpty?: boolean
  onAddData?: () => void
  analysisTime?: string | null
}

function Dashboard({ data, isEmpty = false, onAddData, analysisTime }: Props) {
  const { portfolio, marketIndex, stockAnalyses, overallRecommendation } = data
  const [expandedStock, setExpandedStock] = useState<number | null>(null)

  const formatNumber = (num: number, decimals = 2) => {
    return num.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
  }

  const getChangeClass = (value: number) => value >= 0 ? 'up' : 'down'
  const getChangeIcon = (value: number) => value >= 0 ? '▲' : '▼'

  // 格式化分析时间
  const formatAnalysisTime = (isoTime: string | null | undefined) => {
    if (!isoTime) return ''
    const date = new Date(isoTime)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 空状态展示
  if (isEmpty) {
    return (
      <div className="dashboard">
        <div className="empty-state">
          <div className="empty-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
              <path d="M6 8h.01M6 12h.01M6 16h.01M10 8h8M10 12h8M10 16h8"/>
            </svg>
          </div>
          <h3 className="empty-title">暂无持仓数据</h3>
          <p className="empty-desc">
            录入您的股票持仓信息，系统将为您提供：<br/>
            智能技术分析 · 止盈止损策略 · 实时盈亏监控
          </p>
          <button className="btn btn-primary btn-lg" onClick={onAddData}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            录入持仓数据
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      {/* 分析时间标签 */}
      {analysisTime && (
        <div className="analysis-time-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>数据更新于 {formatAnalysisTime(analysisTime)}</span>
        </div>
      )}

      {/* 顶部统计卡片 */}
      <div className="stats-grid">
        {/* 大盘指数卡片 */}
        <div className="stat-card market-card">
          <div className="stat-header">
            <span className="stat-label">大盘行情</span>
            <span className={`tag tag-${marketIndex.change >= 0 ? 'up' : 'down'}`}>
              {marketIndex.change >= 0 ? '上涨' : '下跌'}
            </span>
          </div>
          <div className="market-info">
            <div className="market-name">{marketIndex.name}</div>
            <div className="market-code">{marketIndex.code}</div>
          </div>
          <div className={`market-price ${getChangeClass(marketIndex.change)}`}>
            {formatNumber(marketIndex.current, 2)}
          </div>
          <div className={`market-change ${getChangeClass(marketIndex.change)}`}>
            <span className="change-value">
              {getChangeIcon(marketIndex.change)}{formatNumber(Math.abs(marketIndex.change), 2)}
            </span>
            <span className="change-rate">
              ({marketIndex.change >= 0 ? '+' : ''}{marketIndex.changeRate}%)
            </span>
          </div>
          <div className="market-mini-chart">
            <svg viewBox="0 0 100 30" preserveAspectRatio="none">
              <path 
                d={marketIndex.change >= 0 
                  ? "M0,25 L10,22 L20,18 L30,20 L40,15 L50,17 L60,12 L70,14 L80,8 L90,10 L100,5"
                  : "M0,5 L10,8 L20,12 L30,10 L40,15 L50,13 L60,18 L70,16 L80,22 L90,20 L100,25"
                }
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2"
                className={getChangeClass(marketIndex.change)}
              />
            </svg>
          </div>
        </div>

        {/* 总市值卡片 */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">持仓总市值</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="1" x2="12" y2="23"/>
              <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
            </svg>
          </div>
          <div className="stat-value">¥ {formatNumber(portfolio.totalMarketValue)}</div>
          <div className="stat-footer">
            <span className="stat-sub">持仓盈亏</span>
            <span className={`stat-change ${getChangeClass(portfolio.totalProfitLoss)}`}>
              {portfolio.totalProfitLoss >= 0 ? '+' : ''}¥ {formatNumber(portfolio.totalProfitLoss)}
            </span>
          </div>
        </div>

        {/* 盈亏率卡片 */}
        <div className="stat-card">
          <div className="stat-header">
            <span className="stat-label">盈亏率</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
              <polyline points="17 6 23 6 23 12"/>
            </svg>
          </div>
          <div className={`stat-value ${getChangeClass(portfolio.totalProfitRate)}`}>
            {portfolio.totalProfitRate >= 0 ? '+' : ''}{formatNumber(portfolio.totalProfitRate)}%
          </div>
          <div className="stat-footer">
            <span className="stat-sub">持仓数量</span>
            <span className="stat-normal">{portfolio.positions.length} 只</span>
          </div>
        </div>

        {/* 总体建议卡片 */}
        <div className="stat-card recommendation-card">
          <div className="stat-header">
            <span className="stat-label">总体建议</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div className={`recommendation-action ${overallRecommendation.action === '买入' ? 'buy' : overallRecommendation.action === '卖出' ? 'sell' : 'hold'}`}>
            {overallRecommendation.action}
          </div>
          <div className="recommendation-confidence">
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ width: `${overallRecommendation.confidence}%` }}
              />
            </div>
            <span>置信度 {overallRecommendation.confidence}%</span>
          </div>
          <div className="recommendation-reason">{overallRecommendation.reason}</div>
        </div>
      </div>

      {/* 图表分析区域 */}
      {stockAnalyses.length > 0 && (
        <div className="charts-section">
          <div className="section-title-group">
            <h3 className="section-title">持仓分析</h3>
          </div>
          
          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-title">持仓分布</div>
              <PortfolioPieChart positions={portfolio.positions} />
            </div>
            
            <div className="chart-card">
              <div className="chart-title">盈亏排行</div>
              <ProfitLossChart stocks={stockAnalyses} />
            </div>
          </div>
        </div>
      )}

      {/* 个股分析列表 */}
      <div className="stocks-section">
        <div className="section-title-group">
          <h3 className="section-title">个股分析</h3>
          <span className="section-count">{stockAnalyses.length} 只股票</span>
        </div>

        <div className="stocks-list">
          {stockAnalyses.map((stock, index) => (
            <StockCard 
              key={index}
              stock={stock}
              index={index}
              isExpanded={expandedStock === index}
              onToggle={() => setExpandedStock(expandedStock === index ? null : index)}
              formatNumber={formatNumber}
              getChangeClass={getChangeClass}
              getChangeIcon={getChangeIcon}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

/* 个股卡片组件 */
interface StockCardProps {
  stock: StockAnalysis
  index: number
  isExpanded: boolean
  onToggle: () => void
  formatNumber: (num: number, decimals?: number) => string
  getChangeClass: (value: number) => string
  getChangeIcon: (value: number) => string
}

function StockCard({ stock, index: _index, isExpanded, onToggle, formatNumber, getChangeClass, getChangeIcon }: StockCardProps) {
  const { position, quote, analysis, recommendation, strategy } = stock

  return (
    <div className={`stock-card ${isExpanded ? 'expanded' : ''}`}>
      {/* 卡片头部 - 始终显示 */}
      <div className="stock-card-header" onClick={onToggle}>
        <div className="stock-basic">
          <div className="stock-name-row">
            <span className="stock-name">{position.name}</span>
            <span className="stock-symbol">{position.symbol}</span>
          </div>
          <div className="stock-price-row">
            <span className="stock-price">{formatNumber(quote.current, 2)}</span>
            <span className={`stock-change ${getChangeClass(quote.changeRate)}`}>
              {getChangeIcon(quote.changeRate)}{quote.changeRate}%
            </span>
          </div>
        </div>

        <div className="stock-holding">
          <div className="holding-item">
            <span className="holding-label">持仓成本</span>
            <span className="holding-value">{formatNumber(position.avgCost, 2)}</span>
          </div>
          <div className="holding-item">
            <span className="holding-label">当前市值</span>
            <span className="holding-value">{formatNumber(position.marketValue)}</span>
          </div>
          <div className="holding-item">
            <span className="holding-label">持仓盈亏</span>
            <span className={`holding-value ${getChangeClass(position.profitLoss)}`}>
              {position.profitLoss >= 0 ? '+' : ''}{formatNumber(position.profitLoss)}
            </span>
          </div>
        </div>

        <div className="stock-action">
          <span className={`action-badge ${recommendation.action === '买入' ? 'buy' : recommendation.action === '卖出' ? 'sell' : 'hold'}`}>
            {recommendation.action}
          </span>
          <svg 
            className={`expand-icon ${isExpanded ? 'rotated' : ''}`}
            width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </div>

      {/* 展开详情区域 */}
      {isExpanded && (
        <div className="stock-card-detail animate-slideUp">
          {/* 技术指标 */}
          <div className="detail-section">
            <div className="detail-section-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 3v18h18"/>
                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
              </svg>
              技术指标
            </div>
            <div className="tech-indicators">
              <div className="indicator-group">
                <span className="indicator-label">MA</span>
                <div className="indicator-values">
                  <span className="indicator-value">MA5: {analysis.technical.ma5}</span>
                  <span className="indicator-value">MA10: {analysis.technical.ma10}</span>
                  <span className="indicator-value">MA20: {analysis.technical.ma20}</span>
                </div>
              </div>
              <div className="indicator-group">
                <span className="indicator-label">MACD</span>
                <div className="indicator-values">
                  <span className="indicator-value">DIF: {analysis.technical.macd.diff.toFixed(2)}</span>
                  <span className="indicator-value">DEA: {analysis.technical.macd.dea.toFixed(2)}</span>
                  <span className="indicator-value">MACD: {analysis.technical.macd.histogram.toFixed(2)}</span>
                </div>
              </div>
              <div className="indicator-group">
                <span className="indicator-label">KDJ</span>
                <div className="indicator-values">
                  <span className="indicator-value">K: {analysis.technical.kdj.k.toFixed(2)}</span>
                  <span className="indicator-value">D: {analysis.technical.kdj.d.toFixed(2)}</span>
                  <span className="indicator-value">J: {analysis.technical.kdj.j.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* 资金流向 */}
          <div className="detail-section">
            <div className="detail-section-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="22" x2="12" y2="2"/>
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
              资金流向
            </div>
            <div className="capital-flow">
              <div className="flow-item">
                <span className="flow-label">主力净流入</span>
                <span className={`flow-value ${getChangeClass(analysis.capital.mainInflow)}`}>
                  {analysis.capital.mainInflow >= 0 ? '+' : ''}{formatNumber(analysis.capital.mainInflow)}
                </span>
              </div>
              <div className="flow-item">
                <span className="flow-label">净流入占比</span>
                <span className={`flow-value ${getChangeClass(analysis.capital.mainInflowRate)}`}>
                  {analysis.capital.mainInflowRate >= 0 ? '+' : ''}{analysis.capital.mainInflowRate}%
                </span>
              </div>
              <div className="flow-item">
                <span className="flow-label">散户净流入</span>
                <span className={`flow-value ${getChangeClass(analysis.capital.retailInflow)}`}>
                  {analysis.capital.retailInflow >= 0 ? '+' : ''}{formatNumber(analysis.capital.retailInflow)}
                </span>
              </div>
            </div>
          </div>

          {/* 策略建议 */}
          <div className="detail-section strategy-section">
            <div className="detail-section-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              止盈止损策略
            </div>
            <div className="strategy-content">
              <div className="strategy-type">
                <span className={`type-badge ${strategy.type === 'fixed' ? 'stable' : strategy.type === 'trailing' ? 'aggressive' : 'balanced'}`}>
                  {strategy.type === 'fixed' ? '固定止盈止损' : strategy.type === 'trailing' ? '追踪止盈止损' : '条件止盈止损'}
                </span>
              </div>
              <div className="strategy-prices">
                {strategy.takeProfitPrice && (
                  <div className="price-item profit">
                    <span className="price-label">止盈价</span>
                    <span className="price-value">{formatNumber(strategy.takeProfitPrice, 2)}</span>
                  </div>
                )}
                {strategy.stopLossPrice && (
                  <div className="price-item loss">
                    <span className="price-label">止损价</span>
                    <span className="price-value">{formatNumber(strategy.stopLossPrice, 2)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 操作理由 */}
          <div className="recommendation-detail">
            <span className="recommend-label">操作理由:</span>
            <span className="recommend-text">{recommendation.reason}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
