import ReactECharts from 'echarts-for-react'
import { StockAnalysis } from '../../types'

interface Props {
  stocks: StockAnalysis[]
}

function ProfitLossChart({ stocks }: Props) {
  const chartData = stocks.map(stock => ({
    name: stock.position.symbol,
    fullName: stock.position.name,
    profitLoss: stock.position.profitLoss,
    profitRate: stock.position.profitRate
  })).sort((a, b) => b.profitRate - a.profitRate)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      backgroundColor: '#1c2128',
      borderColor: '#30363d',
      textStyle: {
        color: '#f0f6fc'
      },
      formatter: (params: any) => {
        const data = params[0]
        const item = chartData[data.dataIndex]
        return `<b>${item.fullName}(${item.name})</b><br/>盈亏: ¥${item.profitLoss.toLocaleString()}<br/>盈亏率: ${item.profitRate >= 0 ? '+' : ''}${item.profitRate.toFixed(2)}%`
      }
    },
    grid: {
      left: '3%',
      right: '8%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: '#21262d',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#6e7681',
        fontSize: 11,
        formatter: (value: number) => {
          if (Math.abs(value) >= 10000) {
            return (value / 10000).toFixed(0) + '万'
          }
          return value.toString()
        }
      }
    },
    yAxis: {
      type: 'category',
      data: chartData.map(d => d.name),
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#8b949e',
        fontSize: 11
      }
    },
    series: [
      {
        name: '盈亏',
        type: 'bar',
        barWidth: '60%',
        data: chartData.map(d => ({
          value: d.profitLoss,
          itemStyle: {
            color: d.profitLoss >= 0 ? '#00c853' : '#ff5252',
            borderRadius: d.profitLoss >= 0 ? [0, 4, 4, 0] : [4, 0, 0, 4]
          }
        })),
        label: {
          show: true,
          position: 'right',
          color: '#8b949e',
          fontSize: 11,
          formatter: (params: any) => {
            const rate = chartData[params.dataIndex].profitRate
            return `${rate >= 0 ? '+' : ''}${rate.toFixed(2)}%`
          }
        }
      }
    ]
  }

  return (
    <div className="bar-chart-container">
      <ReactECharts 
        option={option} 
        style={{ height: '300px', width: '100%' }}
        opts={{ renderer: 'svg' }}
      />
    </div>
  )
}

export default ProfitLossChart
