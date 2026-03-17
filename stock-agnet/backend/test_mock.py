#!/usr/bin/env python3
"""
测试脚本：模拟用户持仓并调用分析（使用模拟数据）
"""
import random
import sys
sys.path.insert(0, '.')

from models import Portfolio, Position, Recommendation, MarketIndex, StockQuote, TechnicalIndicators, CapitalFlow, MACD, KDJ


def get_mock_data_provider():
    """创建模拟数据提供者"""
    
    class MockDataProvider:
        def get_market_index(self, code="1.000001"):
            return MarketIndex(
                name="上证指数",
                code=code,
                current=3050.25 + random.uniform(-50, 50),
                change=random.uniform(-20, 20),
                changeRate=random.uniform(-1.5, 1.5)
            )
        
        def get_stock_quote(self, symbol):
            base_prices = {
                "600036": 38.50,  # 招商银行
                "600519": 1720.00, # 贵州茅台
                "300750": 178.50,  # 宁德时代
            }
            base = base_prices.get(symbol, 100.0)
            current = base * (1 + random.uniform(-0.05, 0.05))
            return StockQuote(
                symbol=symbol,
                name={"600036": "招商银行", "600519": "贵州茅台", "300750": "宁德时代"}.get(symbol, f"股票{symbol}"),
                current=current,
                open=current * (1 + random.uniform(-0.02, 0.02)),
                high=current * (1 + random.uniform(0, 0.03)),
                low=current * (1 + random.uniform(-0.03, 0)),
                volume=random.randint(1000000, 10000000),
                amount=random.randint(100000000, 1000000000),
                change=current * random.uniform(-0.05, 0.05),
                changeRate=random.uniform(-5, 5)
            )
        
        def get_technical_indicators(self, symbol):
            return TechnicalIndicators(
                ma5=random.uniform(35, 40),
                ma10=random.uniform(34, 39),
                ma20=random.uniform(33, 38),
                ma60=random.uniform(30, 35),
                macd=MACD(
                    diff=random.uniform(-1, 1),
                    dea=random.uniform(-1, 1),
                    histogram=random.uniform(-0.5, 0.5)
                ),
                kdj=KDJ(
                    k=random.uniform(20, 80),
                    d=random.uniform(20, 80),
                    j=random.uniform(0, 100)
                )
            )
        
        def get_capital_flow(self, symbol):
            inflow = random.uniform(-50000000, 50000000)
            return CapitalFlow(
                mainInflow=inflow,
                mainInflowRate=inflow / 100000000,
                retailInflow=-inflow,
                retailInflowRate=-inflow / 100000000
            )
    
    return MockDataProvider()


def test_analysis_with_mock():
    """测试持仓分析（使用模拟数据）"""
    print("开始测试...")
    
    # ====== 模拟用户持仓数据 ======
    portfolio = Portfolio(
        positions=[
            Position(
                symbol="600036",
                name="招商银行",
                quantity=1000,
                avgCost=35.50,
                currentPrice=38.25,
                marketValue=38250,
                profitLoss=2750,
                profitRate=7.75
            ),
            Position(
                symbol="600519",
                name="贵州茅台",
                quantity=50,
                avgCost=1650.00,
                currentPrice=1720.00,
                marketValue=86000,
                profitLoss=3500,
                profitRate=4.24
            ),
            Position(
                symbol="300750",
                name="宁德时代",
                quantity=200,
                avgCost=195.00,
                currentPrice=178.50,
                marketValue=35700,
                profitLoss=-3300,
                profitRate=-8.46
            )
        ],
        totalMarketValue=159950,
        totalProfitLoss=2950,
        totalProfitRate=1.88
    )
    
    print("=" * 60)
    print("用户持仓数据（模拟）")
    print("=" * 60)
    print(f"持仓股票数量: {len(portfolio.positions)}")
    print(f"总市值: {portfolio.totalMarketValue:,.2f} 元")
    print(f"浮动盈亏: {portfolio.totalProfitLoss:,.2f} 元 ({portfolio.totalProfitRate:.2f}%)")
    print()
    
    for pos in portfolio.positions:
        print(f"  {pos.name}({pos.symbol}): 成本{pos.avgCost}, 当前{pos.currentPrice}, 盈亏{pos.profitRate:.2f}%")
    print()
    
    # ====== 创建模拟数据提供者 ======
    mock_provider = get_mock_data_provider()
    
    # ====== 调用分析引擎 ======
    print("=" * 60)
    print("开始分析...")
    print("=" * 60)
    
    # 获取大盘数据
    market_index = mock_provider.get_market_index()
    print(f"\n大盘行情: {market_index.name} {market_index.current:.2f} ({market_index.changeRate:+.2f}%)")
    
    # 分析每只股票
    stock_analyses = []
    for position in portfolio.positions:
        quote = mock_provider.get_stock_quote(position.symbol)
        technical = mock_provider.get_technical_indicators(position.symbol)
        capital = mock_provider.get_capital_flow(position.symbol)
        
        # 生成操作建议
        recommendation = _generate_recommendation(position, quote, technical, capital)
        strategy = _generate_strategy(position, recommendation)
        
        stock_analyses.append(type('StockAnalysis', (), {
            'position': position,
            'quote': quote,
            'analysis': type('Analysis', (), {
                'technical': technical,
                'capital': capital,
                'news': []
            }),
            'recommendation': recommendation,
            'strategy': strategy
        })())
    
    # 生成总体建议
    overall = _generate_overall_recommendation(stock_analyses)
    
    print("\n" + "=" * 60)
    print("分析结果")
    print("=" * 60)
    
    for i, sa in enumerate(stock_analyses, 1):
        print(f"\n--- {sa.position.name}({sa.position.symbol}) ---")
        print(f"  当前价格: {sa.quote.current:.2f} | 涨跌幅: {sa.quote.changeRate:+.2f}%")
        print(f"  持仓成本: {sa.position.avgCost:.2f} | 盈亏: {sa.position.profitRate:+.2f}%")
        print(f"  技术指标: MA5={sa.analysis.technical.ma5:.2f}, MA10={sa.analysis.technical.ma10:.2f}")
        print(f"  资金流向: 主力净流入 {sa.analysis.capital.mainInflow:,.0f} ({sa.analysis.capital.mainInflowRate:+.2f}%)")
        print(f"  >>> 操作建议: {sa.recommendation.action} (置信度: {sa.recommendation.confidence:.0f}%)")
        print(f"  >>> 原因: {sa.recommendation.reason}")
        print(f"  >>> 止盈价: {sa.strategy['takeProfitPrice']} | 止损价: {sa.strategy['stopLossPrice']}")
    
    print("\n" + "=" * 60)
    print("总体建议")
    print("=" * 60)
    print(f"操作: {overall.action}")
    print(f"置信度: {overall.confidence:.0f}%")
    print(f"理由: {overall.reason}")


def _generate_recommendation(position, quote, technical, capital):
    """生成操作建议"""
    score = 0
    reasons = []
    
    # 技术面分析
    if technical.ma5 > technical.ma10 > technical.ma20:
        score += 2
        reasons.append("均线多头排列")
    elif technical.ma5 < technical.ma10 < technical.ma20:
        score -= 2
        reasons.append("均线空头排列")
    
    # MACD分析
    if technical.macd.histogram > 0:
        score += 1
        reasons.append("MACD金叉")
    elif technical.macd.histogram < 0:
        score -= 1
        reasons.append("MACD死叉")
    
    # 资金流向分析
    if capital.mainInflow > 0:
        score += 1
        reasons.append("主力资金净流入")
    elif capital.mainInflow < 0:
        score -= 1
        reasons.append("主力资金净流出")
    
    # 涨跌分析
    if quote.changeRate > 3:
        score -= 1
        reasons.append("短期涨幅较大")
    elif quote.changeRate < -3:
        score += 1
        reasons.append("短期回调")
    
    # 持仓盈亏分析
    if position.profitRate > 10:
        score -= 1
        reasons.append("盈利较多")
    elif position.profitRate < -5:
        score += 1
        reasons.append("亏损较大")
    
    # 生成建议
    if score >= 3:
        action = "买入"
        confidence = min(90, 60 + score * 5)
    elif score >= 0:
        action = "持有"
        confidence = min(70, 50 + score * 5)
    else:
        action = "卖出"
        confidence = min(90, 60 + abs(score) * 5)
    
    return Recommendation(
        action=action,
        reason="; ".join(reasons) if reasons else "综合分析建议",
        confidence=confidence
    )


def _generate_strategy(position, recommendation):
    """生成止盈止损策略"""
    current_price = position.currentPrice
    
    if recommendation.action == "卖出":
        stop_loss_rate = 3
        take_profit_rate = 0
    elif recommendation.action == "买入":
        stop_loss_rate = 5
        take_profit_rate = 10
    else:
        stop_loss_rate = 8
        take_profit_rate = 15
    
    return {
        "type": "fixed",
        "stopLossPrice": round(current_price * (1 - stop_loss_rate / 100), 2),
        "stopLossRate": stop_loss_rate,
        "takeProfitPrice": round(current_price * (1 + take_profit_rate / 100), 2) if take_profit_rate > 0 else None,
        "takeProfitRate": take_profit_rate if take_profit_rate > 0 else None
    }


def _generate_overall_recommendation(stock_analyses):
    """生成总体建议"""
    if not stock_analyses:
        return Recommendation(action="持有", reason="暂无持仓数据", confidence=0)
    
    buy_count = sum(1 for s in stock_analyses if s.recommendation.action == "买入")
    sell_count = sum(1 for s in stock_analyses if s.recommendation.action == "卖出")
    hold_count = sum(1 for s in stock_analyses if s.recommendation.action == "持有")
    total = len(stock_analyses)
    avg_confidence = sum(s.recommendation.confidence for s in stock_analyses) / total
    
    if buy_count > sell_count and buy_count > hold_count:
        action = "买入"
        reason = f"{buy_count}/{total}只股票建议买入"
    elif sell_count > buy_count and sell_count > hold_count:
        action = "卖出"
        reason = f"{sell_count}/{total}只股票建议卖出"
    else:
        action = "持有"
        reason = f"{hold_count}/{total}只股票建议持有"
    
    return Recommendation(action=action, reason=reason, confidence=avg_confidence)


if __name__ == "__main__":
    test_analysis_with_mock()
