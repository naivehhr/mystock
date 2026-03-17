import ReactECharts from 'echarts-for-react'

interface KLineData {
  date: string
  open: number
  close: number
  low: number
  high: number
  volume: number
}

interface Props {
  data: KLineData[]
  symbol: string
  name: string
}

function StockKLineChart({ data, symbol, name }: Props) {
  // 准备K线数据
  const dates = data.map(d => d.date)
  const kLineData = data.map(d => [d.open, d.close, d.low, d.high])
  const volumes = data.map((d) => ({
    value: d.volume,
    itemStyle: {
      color: d.close >= d.open ? '#00c853' : '#ff5252',
      opacity: 0.5
    }
  }))

  // 计算移动平均线
  const ma5: (number | null)[] = []
  const ma10: (number | null)[] = []
  const ma20: (number | null)[] = []

  for (let i = 0; i < data.length; i++) {
    if (i < 4) {
      ma5.push(null)
    } else {
      const sum = data.slice(i - 4, i + 1).reduce((acc, d) => acc + d.close, 0)
      ma5.push(sum / 5)
    }

    if (i < 9) {
      ma10.push(null)
    } else {
      const sum = data.slice(i - 9, i + 1).reduce((acc, d) => acc + d.close, 0)
      ma10.push(sum / 10)
    }

    if (i < 19) {
      ma20.push(null)
    } else {
      const sum = data.slice(i - 19, i + 1).reduce((acc, d) => acc + d.close, 0)
      ma20.push(sum / 20)
    }
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#8b949e'
        }
      },
      backgroundColor: '#1c2128',
      borderColor: '#30363d',
      textStyle: {
        color: '#f0f6fc'
      },
      formatter: (params: any) => {
        const kLineData = params.find((p: any) => p.seriesName === 'K线')
        if (!kLineData) return ''
        
        const data = kLineData.data
        const date = kLineData.axisValue
        const volume = params.find((p: any) => p.seriesName === '成交量')
        
        return `<b>${name}(${symbol})</b><br/>
          日期: ${date}<br/>
          开盘: ¥${data[0].toFixed(2)}<br/>
          收盘: ¥${data[1].toFixed(2)}<br/>
          最低: ¥${data[2].toFixed(2)}<br/>
          最高: ¥${data[3].toFixed(2)}<br/>
          成交量: ${(volume?.value / 10000).toFixed(2)}万`
      }
    },
    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20'],
      top: 0,
      textStyle: {
        color: '#8b949e',
        fontSize: 11
      }
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '68%',
        height: '18%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { 
          show: true,
          color: '#6e7681',
          fontSize: 10,
          formatter: (value: string) => value.slice(5)
        },
        splitLine: { show: false }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        boundaryGap: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        splitLine: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: '#6e7681',
          fontSize: 10,
          formatter: (value: number) => value.toFixed(0)
        },
        splitLine: {
          lineStyle: {
            color: '#21262d',
            type: 'dashed'
          }
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        splitLine: {
          lineStyle: {
            color: '#21262d',
            type: 'dashed'
          }
        }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 60,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: kLineData,
        itemStyle: {
          color: '#00c853',
          color0: '#ff5252',
          borderColor: '#00c853',
          borderColor0: '#ff5252'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#58a6ff'
        },
        symbol: 'none'
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10,
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#f0883e'
        },
        symbol: 'none'
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma20,
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#a371f7'
        },
        symbol: 'none'
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        barWidth: '60%'
      }
    ]
  }

  return (
    <div className="kline-chart-container">
      <ReactECharts 
        option={option} 
        style={{ height: '400px', width: '100%' }}
        opts={{ renderer: 'svg' }}
      />
    </div>
  )
}

export default StockKLineChart
