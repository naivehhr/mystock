import ReactECharts from 'echarts-for-react'
import { Position } from '../../types'

interface Props {
  positions: Position[]
}

function PortfolioPieChart({ positions }: Props) {
  const chartData = positions.map(pos => ({
    name: `${pos.name}(${pos.symbol})`,
    value: pos.marketValue
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1c2128',
      borderColor: '#30363d',
      textStyle: {
        color: '#f0f6fc'
      },
      formatter: (params: any) => {
        const total = params.data.value
        const percent = ((params.data.value / total) * 100).toFixed(2)
        return `<b>${params.name}</b><br/>市值: ¥${total.toLocaleString()}<br/>占比: ${percent}%`
      }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: {
        color: '#8b949e',
        fontSize: 11
      },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 8
    },
    series: [
      {
        name: '持仓分布',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#161b22',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#f0f6fc'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: chartData,
        color: [
          '#00d4aa',
          '#58a6ff',
          '#f0883e',
          '#a371f7',
          '#ff7b72',
          '#79c0ff',
          '#7ee787',
          '#ffa657',
          '#ff9f1c',
          '#ff6b6b'
        ]
      }
    ]
  }

  return (
    <div className="pie-chart-container">
      <ReactECharts 
        option={option} 
        style={{ height: '280px', width: '100%' }}
        opts={{ renderer: 'svg' }}
      />
    </div>
  )
}

export default PortfolioPieChart
