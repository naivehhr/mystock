#!/usr/bin/env python3
"""
测试分析引擎功能
"""
import sys
sys.path.insert(0, '.')

from models import Portfolio, Position
from services.analysis import analysis_engine
from data_providers.east_money import data_provider


def test_full_analysis():
    """测试完整分析流程"""
    print("开始测试分析引擎...")
    
    # 创建测试持仓数据
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
    print("测试持仓数据")
    print("=" * 60)
    print(f"持仓股票数量: {len(portfolio.positions)}")
    print(f"总市值: {portfolio.totalMarketValue:,.2f} 元")
    print(f"浮动盈亏: {portfolio.totalProfitLoss:,.2f} 元 ({portfolio.totalProfitRate:.2f}%)")
    print()
    
    for pos in portfolio.positions:
        print(f"  {pos.name}({pos.symbol}): 成本{pos.avgCost}, 当前{pos.currentPrice}, 盈亏{pos.profitRate:.2f}%")
    print()
    
    # 使用分析引擎进行分析
    print("=" * 60)
    print("开始分析...")
    print("=" * 60)
    
    # 获取大盘数据
    try:
        market_index = data_provider.get_market_index()
        print(f"\n大盘行情: {market_index.name} {market_index.current:.2f} ({market_index.changeRate:+.2f}%)")
    except Exception as e:
        print(f"\n获取大盘数据失败: {e}")
        market_index = None
    
    # 分析持仓组合
    stock_analyses = analysis_engine.analyze_portfolio(portfolio)
    
    print("\n" + "=" * 60)
    print("个股分析结果")
    print("=" * 60)
    
    for i, analysis in enumerate(stock_analyses, 1):
        print(f"\n--- {analysis.position.name}({analysis.position.symbol}) ---")
        print(f"  当前价格: {analysis.quote.current:.2f} | 涨跌幅: {analysis.quote.changeRate:+.2f}%")
        print(f"  持仓成本: {analysis.position.avgCost:.2f} | 盈亏: {analysis.position.profitRate:+.2f}%")
        print(f"  技术指标: MA5={analysis.analysis.technical.ma5:.2f}, MA10={analysis.analysis.technical.ma10:.2f}")
        print(f"  MACD: {analysis.analysis.technical.macd.histogram:+.2f} | KDJ: {analysis.analysis.technical.kdj.k:.1f}")
        print(f"  资金流向: 主力净流入 {analysis.analysis.capital.mainInflow:,.0f} ({analysis.analysis.capital.mainInflowRate:+.2f}%)")
        print(f"  >>> 操作建议: {analysis.recommendation.action} (置信度: {analysis.recommendation.confidence:.0f}%)")
        print(f"  >>> 原因: {analysis.recommendation.reason}")
        print(f"  >>> 止盈价: {analysis.strategy.takeProfitPrice} | 止损价: {analysis.strategy.stopLossPrice}")
    
    # 生成总体建议
    overall_recommendation = analysis_engine.generate_overall_recommendation(stock_analyses)
    
    print("\n" + "=" * 60)
    print("总体投资建议")
    print("=" * 60)
    print(f"操作建议: {overall_recommendation.action}")
    print(f"置信度: {overall_recommendation.confidence:.0f}%")
    print(f"理由: {overall_recommendation.reason}")
    
    print("\n测试完成!")


def test_single_stock_analysis():
    """测试单只股票分析"""
    print("\n" + "=" * 60)
    print("测试单只股票分析")
    print("=" * 60)
    
    position = Position(
        symbol="600036",
        name="招商银行",
        quantity=1000,
        avgCost=35.50,
        currentPrice=38.25,
        marketValue=38250,
        profitLoss=2750,
        profitRate=7.75
    )
    
    analysis = analysis_engine.analyze_stock(position)
    
    print(f"股票: {analysis.position.name}({analysis.position.symbol})")
    print(f"当前价格: {analysis.quote.current:.2f}")
    print(f"操作建议: {analysis.recommendation.action} ({analysis.recommendation.confidence:.0f}%)")
    print(f"建议原因: {analysis.recommendation.reason}")


if __name__ == "__main__":
    test_full_analysis()
    test_single_stock_analysis()
