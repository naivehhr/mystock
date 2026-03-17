import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import PortfolioUploadModal from './components/PortfolioUploadModal'
import Dashboard from './pages/Dashboard'
import { Portfolio, AnalysisResult } from './types'

// 历史数据响应类型
interface HistoryResponse {
  data: AnalysisResult
  analysisTime: string
}

// 默认大盘数据
const defaultMarketIndex = {
  name: '上证指数',
  code: '000001',
  current: 0,
  change: 0,
  changeRate: 0
}

// 默认分析结果（空状态）
const emptyAnalysisResult: AnalysisResult = {
  portfolio: {
    positions: [],
    totalMarketValue: 0,
    totalProfitLoss: 0,
    totalProfitRate: 0
  },
  marketIndex: defaultMarketIndex,
  stockAnalyses: [],
  overallRecommendation: {
    action: '持有',
    reason: '暂无持仓数据，请录入持仓信息开始分析',
    confidence: 0
  }
}

function App() {
  const [, setPortfolio] = useState<Portfolio | null>(null)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)
  const [showClearConfirm, setShowClearConfirm] = useState(false)
  const [analysisTime, setAnalysisTime] = useState<string | null>(null)

  // 页面加载时获取历史分析结果
  useEffect(() => {
    fetchHistoryAnalysis()
  }, [])

  const fetchHistoryAnalysis = async () => {
    try {
      const response = await fetch('/api/portfolio/history')
      if (response.ok) {
        const result: HistoryResponse = await response.json()
        if (result && result.data && result.data.portfolio && result.data.portfolio.positions.length > 0) {
          setAnalysisResult(result.data)
          setAnalysisTime(result.analysisTime)
        }
      }
    } catch (error) {
      console.log('暂无历史数据')
    } finally {
      setIsInitializing(false)
    }
  }

  const handlePortfolioUpload = async (data: Portfolio) => {
    setPortfolio(data)
    setLoading(true)
    try {
      const response = await fetch('/api/portfolio/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      const result = await response.json()
      setAnalysisResult(result)
    } catch (error) {
      console.error('分析失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    setPortfolio(null)
    setAnalysisResult(null)
    setAnalysisTime(null)
    setShowClearConfirm(false)
    // 调用后端清空历史数据
    try {
      await fetch('/api/portfolio/clear', { method: 'POST' })
    } catch (error) {
      console.error('清空数据失败:', error)
    }
  }

  // 显示的数据：有分析结果用分析结果，否则用空状态
  const displayData = analysisResult || emptyAnalysisResult
  // 是否有真实数据
  const hasData = analysisResult !== null && analysisResult.portfolio.positions.length > 0

  return (
    <Layout>
      <div className="app-container">
        {/* 顶部操作栏 */}
        <div className="app-header-bar">
          <div className="header-info">
            <h1 className="page-title">持仓分析</h1>
            <p className="page-subtitle">
              {hasData 
                ? `共 ${displayData.portfolio.positions.length} 只持仓，总市值 ¥${displayData.portfolio.totalMarketValue.toLocaleString()}`
                : '录入持仓数据，获取智能分析建议'
              }
            </p>
          </div>
          <div className="header-actions">
            {hasData && (
              <button className="btn btn-ghost btn-danger" onClick={() => setShowClearConfirm(true)}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
                清空数据
              </button>
            )}
            <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              {hasData ? '添加持仓' : '录入数据'}
            </button>
          </div>
        </div>

        {/* Dashboard 始终显示 */}
        <div className="dashboard-wrapper">
          {isInitializing ? (
            <div className="loading-overlay">
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p className="loading-text">正在加载...</p>
              </div>
            </div>
          ) : loading ? (
            <div className="loading-overlay">
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <div className="loading-content">
                  <p className="loading-text">正在分析持仓数据...</p>
                  <p className="loading-subtext">正在获取实时行情、计算技术指标、生成策略建议</p>
                  <div className="loading-progress">
                    <div className="loading-progress-bar"></div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <Dashboard 
              data={displayData} 
              isEmpty={!hasData}
              onAddData={() => setIsModalOpen(true)}
              analysisTime={analysisTime}
            />
          )}
        </div>

        {/* 录入数据弹窗 */}
        <PortfolioUploadModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onUpload={handlePortfolioUpload}
        />

        {/* 清空确认弹窗 */}
        {showClearConfirm && (
          <div className="modal-overlay" onClick={() => setShowClearConfirm(false)}>
            <div className="modal-content modal-sm" onClick={e => e.stopPropagation()}>
              <div className="modal-header">
                <h3 className="modal-title">确认清空</h3>
              </div>
              <div className="modal-body">
                <p className="confirm-text">确定要清空所有持仓数据吗？此操作无法撤销。</p>
              </div>
              <div className="modal-footer">
                <button className="btn btn-ghost" onClick={() => setShowClearConfirm(false)}>
                  取消
                </button>
                <button className="btn btn-danger" onClick={handleReset}>
                  确认清空
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default App
