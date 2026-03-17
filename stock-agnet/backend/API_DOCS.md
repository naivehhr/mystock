# API 数据结构说明

## Portfolio (持仓组合)

```json
{
  "positions": [...],
  "totalMarketValue": 220000,
  "totalProfitLoss": 4000,
  "totalProfitRate": 1.85
}
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| positions | Position[] | 持仓股票列表 | - |
| totalMarketValue | float | 总市值(元) | 220000 |
| totalProfitLoss | float | 总盈亏(元) | 4000 |
| totalProfitRate | float | 总盈亏率(%) | 1.85 |

---

## Position (持仓股票)

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "quantity": 100,
  "avgCost": 1800,
  "currentPrice": 1850,
  "marketValue": 185000,
  "profitLoss": 5000,
  "profitRate": 2.78
}
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| symbol | string | 股票代码(6位数字) | 600519 |
| name | string | 股票名称 | 贵州茅台 |
| quantity | int | 持股数量(股) | 100 |
| avgCost | float | 平均成本(元) | 1800 |
| currentPrice | float | 当前价格(元) | 1850 |
| marketValue | float | 市值(元) | 185000 |
| profitLoss | float | 盈亏金额(元) | 5000 |
| profitRate | float | 盈亏率(%) | 2.78 |

---

## StockQuote (股票行情)

```json
{
  "symbol": "600519",
  "name": "贵州茅台",
  "current": 1850.0,
  "open": 1820.0,
  "high": 1860.0,
  "low": 1810.0,
  "volume": 3500000,
  "amount": 6400000000,
  "change": 30.0,
  "changeRate": 1.65
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| symbol | string | 股票代码 |
| name | string | 股票名称 |
| current | float | 当前价 |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| volume | float | 成交量(手) |
| amount | float | 成交额(元) |
| change | float | 涨跌额 |
| changeRate | float | 涨跌幅(%) |

---

## TechnicalIndicators (技术指标)

```json
{
  "ma5": 1820.5,
  "ma10": 1805.2,
  "ma20": 1780.8,
  "ma60": 1750.3,
  "macd": {
    "diff": 5.2,
    "dea": 3.8,
    "histogram": 1.4
  },
  "kdj": {
    "k": 72.5,
    "d": 65.3,
    "j": 86.9
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| ma5 | float | 5日均线 |
| ma10 | float | 10日均线 |
| ma20 | float | 20日均线 |
| ma60 | float | 60日均线 |
| macd | MACD | MACD指标 |
| kdj | KDJ | KDJ指标 |

#### MACD 子字段
- diff: DIFF线 (快线)
- dea: DEA线 (慢线)
- histogram: 柱状图

#### KDJ 子字段
- k: K值
- d: D值
- j: J值

---

## CapitalFlow (资金流向)

```json
{
  "mainInflow": 50000000,
  "mainInflowRate": 5.0,
  "retailInflow": -50000000,
  "retailInflowRate": -5.0
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| mainInflow | float | 主力净流入(元) |
| mainInflowRate | float | 主力净流入率(%) |
| retailInflow | float | 散户净流入(元) |
| retailInflowRate | float | 散户净流入率(%) |

---

## Recommendation (操作建议)

```json
{
  "action": "买入",
  "reason": "均线多头排列;MACD金叉;主力资金净流入",
  "confidence": 75
}
```

### 字段说明

| 字段 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| action | string | 操作建议 | 买入/卖出/持有 |
| reason | string | 建议原因 | - |
| confidence | float | 置信度(%) | 0-100 |

---

## API 接口

### 分析持仓
- **POST** `/api/portfolio/analyze`
- **Body**: Portfolio JSON

### 保存持仓
- **POST** `/api/portfolio/save`
- **Body**: `{ "name": "组合名", "portfolio": {...} }`

### 获取持仓列表
- **GET** `/api/portfolio/list`

### 获取持仓详情
- **GET** `/api/portfolio/{id}`

### 删除持仓
- **DELETE** `/api/portfolio/{id}`

### 获取分析历史
- **GET** `/api/portfolio/history/{id}`

---

# 分析策略说明

## 评分体系

系统采用**综合评分**方式，根据多个维度对股票进行打分：

### 1. 技术面分析 (权重较高)

| 指标 | 条件 | 分数 | 说明 |
|------|------|------|------|
| **均线多头排列** | ma5 > ma10 > ma20 | +2 | 短期均线在长期均线上方，看涨 |
| **均线空头排列** | ma5 < ma10 < ma20 | -2 | 短期均线在长期均线下方，看跌 |

### 2. MACD指标

| 条件 | 分数 | 说明 |
|------|------|------|
| histogram > 0 (金叉) | +1 | DIF上穿DEA，看涨 |
| histogram < 0 (死叉) | -1 | DIF下穿DEA，看跌 |

### 3. KDJ指标

| 条件 | 分数 | 说明 |
|------|------|------|
| K < 20 (超卖) | +1 | 股价可能反弹 |
| K > 80 (超买) | -1 | 股价可能回调 |

### 4. 资金流向

| 条件 | 分数 | 说明 |
|------|------|------|
| 主力资金净流入 | +1 | 主力买入，看涨 |
| 主力资金净流出 | -1 | 主力卖出，看跌 |

### 5. 短期涨跌

| 条件 | 分数 | 说明 |
|------|------|------|
| 涨幅 > 3% | -1 | 短期涨幅过大，可能回调 |
| 跌幅 > 3% | +1 | 短期回调，可能反弹 |

### 6. 持仓盈亏

| 条件 | 分数 | 说明 |
|------|------|------|
| 盈利 > 10% | -1 | 盈利较多，可能止盈 |
| 亏损 > 5% | +1 | 亏损较大，可能反弹 |

---

## 建议生成规则

根据综合评分生成操作建议：

| 评分 | 建议 | 置信度 |
|------|------|--------|
| >= 3 | **买入** | 60 + 评分×5 (最高90) |
| 0 ~ 2 | **持有** | 50 + 评分×5 (最高70) |
| < 0 | **卖出** | 60 + |评分|×5 (最高90) |

---

## 止盈止损策略

根据建议类型自动生成止盈止损价格：

| 建议 | 止损率 | 止盈率 |
|------|--------|--------|
| 买入 | 5% | 10% |
| 持有 | 8% | 15% |
| 卖出 | 3% | 0% |

### 计算公式
- 止损价 = 当前价 × (1 - 止损率)
- 止盈价 = 当前价 × (1 + 止盈率)

---

## 总体建议生成

根据持仓中所有股票的建议汇总：

| 情况 | 总体建议 |
|------|----------|
| 买入数量 > 卖出数量 且 买入数量 > 持有数量 | 买入 |
| 卖出数量 > 买入数量 且 卖出数量 > 持有数量 | 卖出 |
| 其他情况 | 持有 |

总体置信度 = 所有股票置信度的平均值
