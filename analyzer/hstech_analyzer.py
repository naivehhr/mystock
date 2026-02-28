# -*- coding: utf-8 -*-
"""
恒生科技指数 (HSTECH) 智能分析模块

功能流程：
1. 从东方财富获取实时行情和历史数据
2. 调用 LLM 进行支撑位、压力位和入场时机分析
3. 生成包含分析结果的可视化图表
4. 提供标准化接口供报告生成模块调用

数据来源：东方财富 https://quote.eastmoney.com/gb/zsHSTECH.html
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import os
import logging
import base64
from io import BytesIO
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# 添加 analyzer 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_analyzer import call_ai
from config import LOG_LEVEL

# ============= 日志配置 =============
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# ============= 配置常量 =============
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

SECID = "124.HSTECH"  # 恒生科技指数


@dataclass
class MarketData:
    """市场数据封装"""
    realtime: Optional[Dict]
    history: Optional[pd.DataFrame]
    ma250: Optional[float] = None
    recent_high: Optional[float] = None
    recent_low: Optional[float] = None


class HSTECHDataFetcher:
    """恒生科技指数数据获取器"""
    
    def __init__(self):
        self.secid = SECID
        self.headers = HEADERS
        self.max_retries = 3
    
    def get_realtime_data(self) -> Optional[Dict]:
        """从东方财富获取实时行情数据"""
        logger.info("开始获取恒生科技指数实时行情...")
        
        try:
            url = (
                f"https://push2.eastmoney.com/api/qt/stock/get?"
                f"secid={self.secid}&"
                f"fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f170,f171"
            )
            
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("data"):
                d = data["data"]
                realtime_data = {
                    "名称": "恒生科技指数",
                    "最新价": d.get("f43", 0) / 100,
                    "涨跌幅": d.get("f170", 0) / 100,
                    "涨跌额": d.get("f171", 0) / 100,
                    "今开": d.get("f46", 0) / 100,
                    "最高": d.get("f44", 0) / 100,
                    "最低": d.get("f45", 0) / 100,
                    "昨收": d.get("f60", 0) / 100,
                    "成交量": d.get("f47", 0),
                    "成交额": d.get("f48", 0),
                }
                logger.info(f"实时行情获取成功 - 最新价：{realtime_data['最新价']:.2f}点，涨跌幅：{realtime_data['涨跌幅']:+.2f}%")
                return realtime_data
            else:
                logger.warning("东方财富 API 返回数据为空")
                return None
                
        except Exception as e:
            logger.error(f"实时行情获取失败：{e}")
            return None
    
    def get_history_data(self, days: int = 365) -> Optional[pd.DataFrame]:
        """从东方财富获取历史 K 线数据"""
        logger.info(f"开始获取恒生科技指数历史数据（{days}天）...")
        
        for attempt in range(self.max_retries):
            try:
                url = (
                    f"https://push2his.eastmoney.com/api/qt/stock/kline/get?"
                    f"secid={self.secid}&fields1=f1,f2,f3,f4,f5,f6&"
                    f"fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&"
                    f"klt=101&fqt=1&end=20500101&lmt={days + 10}"
                )
                
                resp = requests.get(url, headers=self.headers, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                
                if data.get("data") and data["data"].get("klines"):
                    klines = data["data"]["klines"]
                    records = []
                    for line in klines:
                        parts = line.split(",")
                        records.append({
                            "日期": parts[0],
                            "开盘": float(parts[1]),
                            "收盘": float(parts[2]),
                            "最高": float(parts[3]),
                            "最低": float(parts[4]),
                            "成交量": float(parts[5]),
                            "成交额": float(parts[6]),
                        })
                    
                    df = pd.DataFrame(records)
                    df["日期"] = pd.to_datetime(df["日期"])
                    df.set_index("日期", inplace=True)
                    
                    logger.info(f"历史数据获取成功 - 共{len(df)}条记录，时间范围：{df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
                    return df
                else:
                    logger.warning(f"东方财富 API 返回数据为空，尝试重试... (第{attempt + 1}/{self.max_retries}次)")
                    if attempt < self.max_retries - 1:
                        import time
                        time.sleep(2)
                        continue
                    return None
                    
            except Exception as e:
                logger.error(f"历史 K 线接口获取失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(2)
                    continue
        
        logger.error("暂无法获取历史 K 线数据（东方财富 K 线接口在当前网络环境下不可用）")
        return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> Tuple[float, float, float]:
        """计算技术指标：250 日均线、近 20 日高点、近 20 日低点"""
        logger.info("计算技术指标...")
        
        ma250 = df["收盘"].rolling(window=250).mean().iloc[-1]
        recent_high = df["最高"].tail(20).max()
        recent_low = df["最低"].tail(20).min()
        
        logger.info(f"技术指标计算完成 - MA250: {ma250:.2f}点，近 20 日高点：{recent_high:.2f}点，近 20 日低点：{recent_low:.2f}点")
        return ma250, recent_high, recent_low


class HSTECHAnalyzer:
    """恒生科技指数 LLM 分析器"""
    
    def __init__(self):
        pass
    
    def analyze(self, realtime_data: Dict, history_data: pd.DataFrame) -> str:
        """调用 LLM 对恒生科技指数进行分析"""
        logger.info("开始调用 LLM 进行智能分析...")
        
        try:
            latest_close = realtime_data["最新价"]
            change_pct = realtime_data["涨跌幅"]
            
            # 计算技术指标
            recent_high = history_data["最高"].tail(20).max()
            recent_low = history_data["最低"].tail(20).min()
            ma250 = history_data["收盘"].rolling(window=250).mean().iloc[-1]
            
            # 准备分析数据摘要
            data_summary = f"""
恒生科技指数 (124.HSTECH) 实时数据：
- 最新价：{latest_close:.2f} 点
- 涨跌幅：{change_pct:+.2f}%
- 开盘：{realtime_data['今开']:.2f} 点
- 最高：{realtime_data['最高']:.2f} 点
- 最低：{realtime_data['最低']:.2f} 点
- 昨收：{realtime_data['昨收']:.2f} 点

技术面数据：
- 近 20 日最高点：{recent_high:.2f} 点
- 近 20 日最低点：{recent_low:.2f} 点
- 250 日均线：{ma250:.2f} 点
- 当前点位：{latest_close:.2f} 点
"""
            
            prompt = f"""你是专业的港股市场分析师，擅长技术分析和实战策略。请基于以下恒生科技指数 (124.HSTECH) 的数据，进行支撑位和压力位分析，并给出入场时机建议：

{data_summary}

分析要求：
1. **支撑位分析**：识别关键支撑位（至少 2 个），说明理由
2. **压力位分析**：识别关键压力位（至少 2 个），说明理由
3. **入场时机建议**：给出具体的入场点位区间和止损位
4. **风险提示**：简要提醒主要风险因素

请用中文回答，保持客观专业，控制在 300 字以内。直接给出分析结果，不需要客套话。"""
            
            logger.debug(f"发送提示词到 LLM，长度：{len(prompt)}字符")
            result = call_ai(prompt)
            
            if result:
                logger.info("LLM 分析调用成功")
                logger.debug(f"LLM 返回结果长度：{len(result)}字符")
                return result
            else:
                logger.warning("LLM 返回结果为空")
                return self._generate_fallback_analysis(realtime_data, history_data)
                
        except Exception as e:
            logger.error(f"LLM 分析调用失败：{e}")
            return self._generate_fallback_analysis(realtime_data, history_data)
    
    def _generate_fallback_analysis(self, realtime_data: Dict, history_data: pd.DataFrame) -> str:
        """生成基于规则的技术分析（备用方案）"""
        logger.info("使用技术分析模板生成备用分析结果...")
        
        latest_close = realtime_data["最新价"]
        change_pct = realtime_data["涨跌幅"]
        recent_high = history_data["最高"].tail(20).max()
        recent_low = history_data["最低"].tail(20).min()
        ma250 = history_data["收盘"].rolling(window=250).mean().iloc[-1]
        
        aggressive_entry_low = int(latest_close * 0.98)
        aggressive_entry_high = int(latest_close * 0.99)
        steady_entry = int(recent_low)
        stop_loss = int(recent_low * 0.97)
        
        analysis = f"""
**技术面分析**：
- 当前点位：{latest_close:.2f} 点，涨跌幅 {change_pct:+.2f}%
- 近 20 日区间：{recent_low:.2f} - {recent_high:.2f} 点
- 长期趋势线：250 日均线 {ma250:.2f} 点

**支撑位**：
1. {recent_low:.0f} 点（近 20 日低点）
2. {int(ma250):.0f} 点（250 日均线）

**压力位**：
1. {recent_high:.0f} 点（近 20 日高点）
2. {int(recent_high * 1.05):.0f} 点（前期平台）

**操作建议**：
- 激进型：可在 {aggressive_entry_low}-{aggressive_entry_high} 点区间轻仓试多
- 稳健型：等待回踩 {steady_entry} 点附近再考虑入场
- 止损位：{stop_loss} 点

*注：此分析基于规则模板生成，仅供参考，投资需谨慎。*
"""
        logger.info("备用分析结果生成成功")
        return analysis


class HSTECHChartGenerator:
    """恒生科技指数图表生成器"""
    
    def __init__(self):
        pass
    
    def generate_analysis_chart(
        self,
        history_data: pd.DataFrame,
        realtime_data: Dict,
        llm_analysis: str,
        output_path: Optional[str] = None,
        return_base64: bool = True
    ) -> Tuple[Optional[str], Optional[str]]:
        """生成技术分析图表（仅 K 线图和技术指标）
        
        Args:
            history_data: 历史数据
            realtime_data: 实时数据
            llm_analysis: LLM 分析结果
            output_path: 输出文件路径（None 则自动生成）
            return_base64: 是否返回 Base64 编码（默认 True）
            
        Returns:
            (file_path, base64_data) 元组
        """
        logger.info("开始生成技术分析图表...")
        
        try:
            # 提取关键数据
            latest_close = realtime_data["最新价"]
            ma250 = history_data["收盘"].rolling(window=250).mean().iloc[-1]
            recent_high = history_data["最高"].tail(20).max()
            recent_low = history_data["最低"].tail(20).min()
            
            # 计算入场点位
            aggressive_entry_low = int(recent_low * 0.98)
            aggressive_entry_high = int(recent_low * 0.99)
            steady_entry = int(recent_low)
            stop_loss = int(recent_low * 0.97)
            
            # 创建图表（保持原始布局）
            fig, ax1 = plt.subplots(figsize=(16, 8))
            
            # ===== 上半部分：K 线图和技术指标 =====
            ax1.plot(history_data.index, history_data["收盘"], label="收盘价", color="blue", linewidth=1.5)
            ax1.plot(history_data.index, history_data["MA250"], label="250 日均线", color="orange", linewidth=1.5, alpha=0.7)
            
            # 标记关键位置
            ax1.axhline(y=recent_low, color="green", linestyle="--", linewidth=2, label=f"支撑位：{recent_low:.0f}点")
            ax1.axhline(y=recent_high, color="red", linestyle="--", linewidth=2, label=f"压力位：{recent_high:.0f}点")
            
            # 填充交易区间
            ax1.fill_between(history_data.index, recent_low, recent_high, alpha=0.15, color="gray", label="近 20 日交易区间")
            
            # 标记入场点位
            ax1.axhline(y=aggressive_entry_low, color="purple", linestyle=":", linewidth=1.5, label=f"激进入场下限：{aggressive_entry_low}")
            ax1.axhline(y=aggressive_entry_high, color="purple", linestyle=":", linewidth=1.5, label=f"激进入场上限：{aggressive_entry_high}")
            ax1.axhline(y=steady_entry, color="cyan", linestyle="-.", linewidth=1.5, label=f"稳健入场位：{steady_entry}")
            ax1.axhline(y=stop_loss, color="black", linestyle=":", linewidth=1, label=f"止损位：{stop_loss}")
            
            # 填充激进入场区间
            ax1.fill_between(history_data.index, aggressive_entry_low, aggressive_entry_high, alpha=0.15, color="purple", label="激进入场区间")
            
            # 当前价位标记
            ax1.axhspan(latest_close - 10, latest_close + 10, alpha=0.2, color="blue", label=f"当前价位：{latest_close:.0f}")
            
            ax1.set_title("恒生科技指数 (HSTECH) - 技术分析图", fontsize=16, fontweight='bold')
            ax1.set_xlabel("日期", fontsize=12)
            ax1.set_ylabel("指数点位", fontsize=12)
            ax1.legend(loc="upper left", bbox_to_anchor=(0.98, 0.98), ncol=1, fontsize=9)
            ax1.grid(True, alpha=0.3)
            
            # 添加标题
            fig.suptitle(
                f"恒生科技指数智能分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                fontsize=18,
                fontweight='bold',
                y=0.995
            )
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            
            # 保存图片到文件
            file_path = None
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "reports",
                    f"hstech_chart_{timestamp}.png"
                )
            
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            logger.info(f"技术分析图表保存成功：{output_path}")
            file_path = output_path
            
            # 转换为 Base64
            base64_data = None
            if return_base64:
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                img_bytes = buf.read()
                base64_data = base64.b64encode(img_bytes).decode('utf-8')
                logger.info("图片已转换为 Base64 编码")
            
            plt.close()
            return file_path, base64_data
            
        except Exception as e:
            logger.error(f"图表生成失败：{e}")
            raise


class HSTECHAnalyzerFacade:
    """恒生科技指数分析外观类 - 提供统一的对外接口"""
    
    def __init__(self):
        self.data_fetcher = HSTECHDataFetcher()
        self.analyzer = HSTECHAnalyzer()
        self.chart_generator = HSTECHChartGenerator()
    
    def generate_full_report(self, save_chart: bool = True, verbose: bool = False) -> Dict:
        """
        生成完整的恒生科技指数分析报告
        
        Args:
            save_chart: 是否保存分析图表
            verbose: 是否输出详细日志（默认 False，只在系统调用时输出关键信息）
            
        Returns:
            包含所有分析结果的字典
        """
        if verbose:
            logger.info("=" * 60)
            logger.info("开始生成恒生科技指数完整分析报告")
            logger.info("=" * 60)
        else:
            logger.info("正在生成恒生科技指数分析报告...")
        
        try:
            # Step 1: 获取实时行情数据
            realtime_data = self.data_fetcher.get_realtime_data()
            if not realtime_data:
                logger.error("实时行情数据获取失败")
                raise ValueError("无法获取实时行情数据")
            
            # Step 2: 获取历史数据
            history_data = self.data_fetcher.get_history_data(days=365)
            if history_data is None or history_data.empty:
                logger.error("历史数据获取失败")
                raise ValueError("无法获取历史数据")
            
            # Step 3: 计算技术指标
            ma250, recent_high, recent_low = self.data_fetcher.calculate_technical_indicators(history_data)
            history_data["MA250"] = history_data["收盘"].rolling(window=250).mean()
            
            # Step 4: 调用 LLM 进行分析
            llm_analysis = self.analyzer.analyze(realtime_data, history_data)
            
            # Step 5: 生成分析图表（同时获取文件路径和 Base64）
            chart_path = None
            chart_base64 = None
            if save_chart:
                chart_path, chart_base64 = self.chart_generator.generate_analysis_chart(
                    history_data=history_data,
                    realtime_data=realtime_data,
                    llm_analysis=llm_analysis,
                    return_base64=True
                )
            
            # 组装完整报告
            report = {
                "realtime_data": realtime_data,
                "history_data": history_data,
                "technical_indicators": {
                    "ma250": ma250,
                    "recent_high": recent_high,
                    "recent_low": recent_low,
                },
                "llm_analysis": llm_analysis,
                "chart_path": chart_path,  # 文件路径（用于存档）
                "chart_base64": chart_base64,  # Base64 编码（用于邮件）
                "timestamp": datetime.now().isoformat(),
            }
            
            if verbose:
                logger.info("恒生科技指数完整分析报告生成成功")
                logger.info("=" * 60)
            else:
                logger.info(f"报告生成完成 - 图表：{chart_path}")
            
            return report
            
        except Exception as e:
            logger.error(f"生成完整报告失败：{e}")
            raise
    
    def get_quick_analysis(self) -> str:
        """
        快速获取分析结果（仅文字分析，不生成图表）
        
        Returns:
            LLM 分析结果字符串
        """
        logger.info("开始快速获取分析结果...")
        
        try:
            # 获取数据
            realtime_data = self.data_fetcher.get_realtime_data()
            if not realtime_data:
                # 使用历史数据的最新值
                history_data = self.data_fetcher.get_history_data(days=5)
                if history_data is None or history_data.empty:
                    raise ValueError("无法获取任何数据")
                
                realtime_data = {
                    "名称": "恒生科技指数",
                    "最新价": history_data["收盘"].iloc[-1],
                    "涨跌幅": 0.0,
                    "今开": history_data["开盘"].iloc[-1],
                    "最高": history_data["最高"].iloc[-1],
                    "最低": history_data["最低"].iloc[-1],
                    "昨收": history_data["收盘"].iloc[-2] if len(history_data) > 1 else history_data["收盘"].iloc[-1],
                }
            
            history_data = self.data_fetcher.get_history_data(days=365)
            if history_data is None or history_data.empty:
                history_data = self.data_fetcher.get_history_data(days=30)
            
            # 调用 LLM 分析
            analysis = self.analyzer.analyze(realtime_data, history_data)
            
            logger.info("快速获取分析结果完成")
            return analysis
            
        except Exception as e:
            logger.error(f"快速获取分析失败：{e}")
            raise


def main():
    """主函数 - 演示完整分析流程"""
    try:
        # 创建分析器实例
        analyzer = HSTECHAnalyzerFacade()
        
        # 生成完整报告（使用 verbose=True 显示详细信息）
        report = analyzer.generate_full_report(save_chart=True, verbose=True)
        
        # 打印报告摘要
        print("\n" + "=" * 60)
        print("📊 恒生科技指数分析报告")
        print("=" * 60)
        
        realtime = report["realtime_data"]
        print(f"\n【实时行情】")
        print(f"  最新价：{realtime['最新价']:.2f} 点")
        print(f"  涨跌幅：{realtime['涨跌幅']:+.2f}%")
        print(f"  成交量：{realtime['成交量']} 手")
        
        tech = report["technical_indicators"]
        print(f"\n【技术指标】")
        print(f"  250 日均线：{tech['ma250']:.2f} 点")
        print(f"  近 20 日高点：{tech['recent_high']:.2f} 点")
        print(f"  近 20 日低点：{tech['recent_low']:.2f} 点")
        
        print(f"\n【LLM 分析结果】")
        print(report["llm_analysis"])
        
        if report["chart_path"]:
            print(f"\n【分析图表】已保存至：{report['chart_path']}")
        if report.get("chart_base64"):
            base64_len = len(report["chart_base64"])
            print(f"【Base64 数据】长度：{base64} 字符（可用于邮件嵌入）")
        
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"程序执行失败：{e}")
        import traceback
        traceback.print_exc()
