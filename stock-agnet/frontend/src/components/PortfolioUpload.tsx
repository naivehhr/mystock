import { useState } from 'react'
import { Portfolio, Position } from '../types'
import { validateStockCode } from '../utils/stockValidation'
import './PortfolioUpload.css'

interface Props {
  onUpload: (data: Portfolio) => void
}

interface PositionForm {
  symbol: string
  name: string
  quantity: string
  avgCost: string
  currentPrice: string
}

const initialPositionForm: PositionForm = {
  symbol: '',
  name: '',
  quantity: '',
  avgCost: '',
  currentPrice: ''
}

function PortfolioUpload({ onUpload }: Props) {
  const [positions, setPositions] = useState<PositionForm[]>([initialPositionForm])
  const [errors, setErrors] = useState<Record<number, Record<string, string>>>({})

  const validatePosition = (pos: PositionForm): Record<string, string> => {
    const newErrors: Record<string, string> = {}
    
    if (!pos.symbol.trim()) {
      newErrors.symbol = '必填'
    } else if (!/^\d{6}$/.test(pos.symbol.trim())) {
      newErrors.symbol = '请输入6位股票代码'
    }
    
    if (!pos.name.trim()) {
      newErrors.name = '必填'
    } else if (pos.symbol.trim() && /^\d{6}$/.test(pos.symbol.trim())) {
      // 验证股票代码和名称是否匹配
      const validation = validateStockCode(pos.symbol.trim(), pos.name.trim())
      if (!validation.valid && validation.message) {
        newErrors.name = validation.message
      }
    }
    
    if (!pos.quantity.trim()) {
      newErrors.quantity = '必填'
    } else if (isNaN(Number(pos.quantity)) || Number(pos.quantity) <= 0) {
      newErrors.quantity = '请输入有效数量'
    }
    
    if (!pos.avgCost.trim()) {
      newErrors.avgCost = '必填'
    } else if (isNaN(Number(pos.avgCost)) || Number(pos.avgCost) <= 0) {
      newErrors.avgCost = '请输入有效价格'
    }
    
    if (pos.currentPrice.trim()) {
      if (isNaN(Number(pos.currentPrice)) || Number(pos.currentPrice) <= 0) {
        newErrors.currentPrice = '请输入有效价格'
      }
    }
    
    return newErrors
  }

  const addPosition = () => {
    setPositions([...positions, { ...initialPositionForm }])
  }

  const removePosition = (index: number) => {
    if (positions.length > 1) {
      setPositions(positions.filter((_, i) => i !== index))
      const newErrors = { ...errors }
      delete newErrors[index]
      setErrors(newErrors)
    }
  }

  const updatePosition = (index: number, field: keyof PositionForm, value: string) => {
    const newPositions = [...positions]
    newPositions[index] = { ...newPositions[index], [field]: value }
    setPositions(newPositions)
    
    // 实时校验股票代码和名称
    const currentPos = newPositions[index]
    if ((field === 'symbol' || field === 'name') && 
        currentPos.symbol.trim() && currentPos.name.trim() &&
        /^\d{6}$/.test(currentPos.symbol.trim())) {
      const validation = validateStockCode(currentPos.symbol.trim(), currentPos.name.trim())
      if (!validation.valid && validation.message) {
        const newErrors = { ...errors }
        if (!newErrors[index]) newErrors[index] = {}
        newErrors[index].name = validation.message
        setErrors(newErrors)
        return
      }
    }
    
    // 清除该字段的错误
    if (errors[index]?.[field]) {
      const newErrors = { ...errors }
      delete newErrors[index][field]
      setErrors(newErrors)
    }
  }

  const handleSubmit = () => {
    // 验证所有持仓
    let hasError = false
    const newErrors: Record<number, Record<string, string>> = {}
    
    positions.forEach((pos, index) => {
      const posErrors = validatePosition(pos)
      if (Object.keys(posErrors).length > 0) {
        newErrors[index] = posErrors
        hasError = true
      }
    })
    
    setErrors(newErrors)
    
    if (hasError) return

    // 转换为Portfolio格式
    const validPositions: Position[] = positions.map(pos => {
      const quantity = Number(pos.quantity)
      const avgCost = Number(pos.avgCost)
      const currentPrice = pos.currentPrice.trim() ? Number(pos.currentPrice) : avgCost
      
      const marketValue = quantity * currentPrice
      const profitLoss = (currentPrice - avgCost) * quantity
      const profitRate = ((currentPrice - avgCost) / avgCost) * 100
      
      return {
        symbol: pos.symbol.trim(),
        name: pos.name.trim(),
        quantity,
        avgCost,
        currentPrice,
        marketValue,
        profitLoss,
        profitRate
      }
    })

    const totalMarketValue = validPositions.reduce((sum, p) => sum + p.marketValue, 0)
    const totalCost = validPositions.reduce((sum, p) => sum + p.avgCost * p.quantity, 0)
    const totalProfitLoss = totalMarketValue - totalCost
    const totalProfitRate = ((totalMarketValue - totalCost) / totalCost) * 100

    const portfolio: Portfolio = {
      positions: validPositions,
      totalMarketValue,
      totalProfitLoss,
      totalProfitRate
    }

    onUpload(portfolio)
  }

  const loadSample = () => {
    const sample: PositionForm[] = [
      { symbol: '600519', name: '贵州茅台', quantity: '100', avgCost: '1800', currentPrice: '1850' },
      { symbol: '000858', name: '五粮液', quantity: '200', avgCost: '180', currentPrice: '175' },
      { symbol: '600036', name: '招商银行', quantity: '500', avgCost: '35', currentPrice: '' }
    ]
    setPositions(sample)
    setErrors({})
  }

  return (
    <div className="portfolio-upload">
      <div className="upload-card">
        {/* 字段说明 */}
        <div className="field-legend">
          <div className="legend-item">
            <span className="legend-mark required"></span>
            <span className="legend-text">为必填字段</span>
          </div>
          <div className="legend-item">
            <span className="legend-mark optional"></span>
            <span className="legend-text">为可选项（填写后可计算盈亏）</span>
          </div>
        </div>

        {/* 持仓表单列表 */}
        <div className="positions-list">
          {positions.map((position, index) => (
            <div key={index} className="position-form-card">
              <div className="position-header">
                <span className="position-number">持仓 {index + 1}</span>
                {positions.length > 1 && (
                  <button 
                    type="button" 
                    className="btn-remove"
                    onClick={() => removePosition(index)}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </button>
                )}
              </div>
              
              <div className="position-fields">
                <div className="field-row">
                  <div className="field-group">
                    <label className="field-label required">股票代码</label>
                    <input
                      type="text"
                      className={`input ${errors[index]?.symbol ? 'error' : ''}`}
                      placeholder="如: 600519"
                      value={position.symbol}
                      onChange={(e) => updatePosition(index, 'symbol', e.target.value)}
                      maxLength={6}
                    />
                    {errors[index]?.symbol && <span className="field-error">{errors[index].symbol}</span>}
                  </div>
                  
                  <div className="field-group">
                    <label className="field-label required">股票名称</label>
                    <input
                      type="text"
                      className={`input ${errors[index]?.name ? 'error' : ''}`}
                      placeholder="如: 贵州茅台"
                      value={position.name}
                      onChange={(e) => updatePosition(index, 'name', e.target.value)}
                    />
                    {errors[index]?.name && <span className="field-error">{errors[index].name}</span>}
                  </div>
                </div>
                
                <div className="field-row">
                  <div className="field-group">
                    <label className="field-label required">持仓数量(股)</label>
                    <input
                      type="number"
                      className={`input ${errors[index]?.quantity ? 'error' : ''}`}
                      placeholder="如: 100"
                      value={position.quantity}
                      onChange={(e) => updatePosition(index, 'quantity', e.target.value)}
                      min="0"
                    />
                    {errors[index]?.quantity && <span className="field-error">{errors[index].quantity}</span>}
                  </div>
                  
                  <div className="field-group">
                    <label className="field-label required">成本价(元)</label>
                    <input
                      type="number"
                      className={`input ${errors[index]?.avgCost ? 'error' : ''}`}
                      placeholder="如: 1800.00"
                      value={position.avgCost}
                      onChange={(e) => updatePosition(index, 'avgCost', e.target.value)}
                      min="0"
                      step="0.01"
                    />
                    {errors[index]?.avgCost && <span className="field-error">{errors[index].avgCost}</span>}
                  </div>
                  
                  <div className="field-group optional-field">
                    <label className="field-label">当前价格(元)</label>
                    <input
                      type="number"
                      className={`input ${errors[index]?.currentPrice ? 'error' : ''}`}
                      placeholder="留空则按成本价计算"
                      value={position.currentPrice}
                      onChange={(e) => updatePosition(index, 'currentPrice', e.target.value)}
                      min="0"
                      step="0.01"
                    />
                    {errors[index]?.currentPrice && <span className="field-error">{errors[index].currentPrice}</span>}
                  </div>
                </div>
              </div>
              
              {/* 实时预览计算结果 */}
              {position.quantity && position.avgCost && (
                <div className="position-preview">
                  <span className="preview-label">预估:</span>
                  <span className="preview-value">
                    市值: ¥{((Number(position.quantity) || 0) * (Number(position.currentPrice) || Number(position.avgCost) || 0)).toLocaleString()}
                  </span>
                  {position.currentPrice && (
                    <span className={`preview-value ${Number(position.currentPrice) >= Number(position.avgCost) ? 'up' : 'down'}`}>
                      盈亏: {Number(position.currentPrice) >= Number(position.avgCost) ? '+' : ''}
                      {(((Number(position.currentPrice) - Number(position.avgCost)) * (Number(position.quantity) || 0))).toFixed(2)}
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* 添加按钮 */}
        <div className="add-position">
          <button type="button" className="btn btn-secondary" onClick={addPosition}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            添加更多持仓
          </button>
          
          <button type="button" className="btn btn-ghost" onClick={loadSample}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            加载示例
          </button>
        </div>

        {/* 提交按钮 */}
        <div className="upload-submit">
          <button 
            type="button"
            className="btn btn-primary btn-lg" 
            onClick={handleSubmit}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            开始智能分析
          </button>
        </div>
      </div>
    </div>
  )
}

export default PortfolioUpload
