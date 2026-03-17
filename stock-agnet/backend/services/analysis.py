"""
多维度分析引擎
提供技术面、基本面、资金面等综合分析
"""
from typing import List
from models import (
    Portfolio, Position, StockQuote, Analysis, TechnicalIndicators,
    CapitalFlow, Recommendation, StockAnalysis, MarketIndex
)
from data_providers.east_money import data_provider


class AnalysisEngine:
    """多维度分析引擎"""
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码格式"""
        symbol = symbol.strip().upper()
        
        # 如果已经是标准格式（SH/SZ开头），直接返回
        if symbol.startswith(('SH', 'SZ')):
            return symbol
        
        # 处理纯数字代码
        if symbol.isdigit():
            if len(symbol) == 6:
                # 上海股票：600xxx, 601xxx, 603xxx, 605xxx, 688xxx, 689xxx
                if symbol.startswith(('600', '601', '603', '605', '688', '689')):
                    return f"SH{symbol}"
                # 深圳股票：其他6位数字
                else:
                    return f"SZ{symbol}"
            elif len(symbol) == 5:
                # 5位数通常是基金或权证
                return f"SZ{symbol}"
        
        # 默认返回原代码
        return symbol
    
    def analyze_portfolio(self, portfolio: Portfolio) -> List[StockAnalysis]:
        """分析整个持仓组合"""
        stock_analyses = []
        
        for position in portfolio.positions:
            analysis = self.analyze_stock(position)
            stock_analyses.append(analysis)
        
        return stock_analyses
    
    def analyze_stock(self, position: Position) -> StockAnalysis:
        """分析单只股票"""
        # 标准化股票代码格式
        normalized_symbol = self._normalize_symbol(position.symbol)
        print(f"分析股票: {position.symbol} -> {normalized_symbol}")
        
        # 获取实时行情
        quote = data_provider.get_stock_quote(normalized_symbol)
        if not quote:
            quote = StockQuote(
                symbol=normalized_symbol,
                name=position.name,
                current=position.currentPrice,
                open=position.currentPrice,
                high=position.currentPrice,
                low=position.currentPrice,
                volume=0,
                amount=0,
                change=0,
                changeRate=0
            )
        
        # 获取技术指标和资金流向
        technical = data_provider.get_technical_indicators(normalized_symbol)
        capital = data_provider.get_capital_flow(normalized_symbol)
        
        # 构建分析对象
        analysis_data = Analysis(
            symbol=normalized_symbol,
            name=position.name,
            technical=technical,
            capital=capital,
            news=[]  # 新闻数据待实现
        )
        
        # 生成操作建议
        recommendation = self._generate_recommendation(position, quote, technical, capital)
        
        # 生成止盈止损策略
        strategy = self._generate_strategy(position, recommendation)
        
        return StockAnalysis(
            position=position,
            quote=quote,
            analysis=analysis_data,
            strategy=strategy,
            recommendation=recommendation
        )
    
    def _generate_recommendation(self, position: Position, quote: StockQuote, 
                               technical: TechnicalIndicators, capital: CapitalFlow) -> Recommendation:
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
        
        # KDJ分析
        if technical.kdj.k < 20:
            score += 1
            reasons.append("KDJ超卖")
        elif technical.kdj.k > 80:
            score -= 1
            reasons.append("KDJ超买")
        
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
    
    def _generate_strategy(self, position: Position, recommendation: Recommendation):
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
    
    def generate_overall_recommendation(self, stock_analyses: List[StockAnalysis]) -> Recommendation:
        """生成总体投资建议"""
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


    def get_market_index_data(self) -> MarketIndex:
        """获取大盘指数数据"""
        # 获取上证指数数据
        quote = data_provider.get_stock_quote("SH000001")
        if not quote:
            # 返回默认数据
            return MarketIndex(
                name="上证指数",
                code="SH000001",
                current=3000.0,
                change=0.0,
                changeRate=0.0
            )
        
        return MarketIndex(
            name=quote.name,
            code="SH000001",
            current=quote.current,
            change=quote.change,
            changeRate=quote.changeRate
        )

# 全局实例
analysis_engine = AnalysisEngine()