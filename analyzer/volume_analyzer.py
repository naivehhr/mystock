# -*- coding: utf-8 -*-
"""
股票成交量特征分析模块

功能：
1. 成交量放大/缩小特征识别
2. 量价关系分析
3. 换手率分析
4. 成交量均线分析

数据来源：东方财富 API
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_fetcher import get_kline_data, get_realtime_quote


def is_morning_session() -> Tuple[bool, str]:
    """判断当前是否处于上午时段（A股交易时段）
    
    Returns:
        (是否上午盘, 说明文字)
    A股交易时段：
        - 上午：9:30-11:30
        - 下午：13:00-15:00
    """
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    # 判断是否在交易时段内
    # 上午盘：9:30 - 11:30
    if (current_hour == 9 and current_minute >= 30) or (10 <= current_hour <= 11):
        if current_hour == 11 and current_minute > 30:
            return False, "上午盘（已过上午交易时段）"
        return True, "上午盘"
    
    # 下午盘：13:00 - 15:00
    if 12 <= current_hour <= 14:
        if current_hour == 14 and current_minute > 30:
            return False, "已收盘"
        return False, "下午盘"
    
    # 非交易时段判断
    if current_hour < 9:
        return False, "盘前"
    elif current_hour == 9 and current_minute < 30:
        return False, "盘前"
    elif current_hour == 11 and current_minute <= 30:
        return False, "午间休市"
    elif current_hour == 12:
        return False, "午间休市"
    elif current_hour == 15 and current_minute <= 30:
        return False, "盘后"
    else:
        return False, "非交易时段"


def calculate_ma(values: List[float], period: int) -> Optional[float]:
    """计算简单移动平均"""
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def analyze_volume特征(history: List[Dict], days: int = 20) -> Dict:
    """分析成交量特征
    
    Args:
        history: K线历史数据列表
        days: 分析天数（默认20天）
    
    Returns:
        成交量特征分析结果字典
    """
    if not history or len(history) < 5:
        return {
            "success": False,
            "error": "数据不足，无法进行成交量分析"
        }
    
    # 准备数据（按日期正序排列）
    sorted_history = sorted(history, key=lambda x: x.get('日期', ''))
    
    # 选取最近N天的数据
    recent_data = sorted_history[-days:] if len(sorted_history) >= days else sorted_history
    
    # 提取成交量和价格数据（成交量单位：手）
    volumes = [float(d.get('成交量', 0)) for d in recent_data]
    closes = [float(d.get('收盘', 0)) for d in recent_data]
    highs = [float(d.get('最高', 0)) for d in recent_data]
    lows = [float(d.get('最低', 0)) for d in recent_data]
    changes = [float(d.get('涨跌幅', 0)) for d in recent_data]
    turnover_rates = [float(d.get('换手率', 0)) for d in recent_data]
    
    # 计算各项指标（成交量单位：手）
    avg_volume_5 = calculate_ma(volumes, 5)  # 5日均量（手）
    avg_volume_10 = calculate_ma(volumes, 10)  # 10日均量（手）
    avg_volume_20 = calculate_ma(volumes, 20)  # 20日均量（手）
    
    current_volume = volumes[-1] if volumes else 0  # 今日成交量（手）
    prev_volume = volumes[-2] if len(volumes) > 1 else 0
    
    # 成交量换算为万手
    current_volume_万手 = current_volume / 10000
    avg_volume_5_万手 = avg_volume_5 / 10000 if avg_volume_5 else None
    avg_volume_10_万手 = avg_volume_10 / 10000 if avg_volume_10 else None
    avg_volume_20_万手 = avg_volume_20 / 10000 if avg_volume_20 else None
    
    # 成交量变化率
    volume_change_ratio = 0
    if prev_volume > 0:
        volume_change_ratio = (current_volume - prev_volume) / prev_volume * 100
    
    # 成交量放大/缩小判断
    is_volume_up = current_volume > avg_volume_5 * 1.5 if avg_volume_5 else False
    is_volume_down = current_volume < avg_volume_5 * 0.5 if avg_volume_5 else False
    
    # 价格变化
    current_price = closes[-1] if closes else 0
    prev_price = closes[-2] if len(closes) > 1 else 0
    price_change = current_price - prev_price
    price_change_pct = changes[-1] if changes else 0
    
    # 近期涨跌趋势
    up_days = sum(1 for c in changes if c > 0)
    down_days = sum(1 for c in changes if c < 0)
    
    # 换手率分析
    avg_turnover = sum(turnover_rates) / len(turnover_rates) if turnover_rates else 0
    current_turnover = turnover_rates[-1] if turnover_rates else 0
    
    # 量价关系分析
    volume_price_analysis = analyze_volume_price_relation(
        volumes, closes, changes
    )
    
    result = {
        "success": True,
        "current_volume": current_volume,
        "current_volume_万手": round(current_volume_万手, 2),
        "avg_volume_5": avg_volume_5,
        "avg_volume_5_万手": round(avg_volume_5_万手, 2) if avg_volume_5_万手 else None,
        "avg_volume_10": avg_volume_10,
        "avg_volume_10_万手": round(avg_volume_10_万手, 2) if avg_volume_10_万手 else None,
        "avg_volume_20": avg_volume_20,
        "avg_volume_20_万手": round(avg_volume_20_万手, 2) if avg_volume_20_万手 else None,
        "volume_change_ratio": volume_change_ratio,
        "is_volume_up": is_volume_up,
        "is_volume_down": is_volume_down,
        "current_price": current_price,
        "price_change": price_change,
        "price_change_pct": price_change_pct,
        "up_days": up_days,
        "down_days": down_days,
        "current_turnover": current_turnover,
        "avg_turnover": avg_turnover,
        "volume_price_relation": volume_price_analysis
    }
    
    return result


def analyze_volume_price_relation(
    volumes: List[float], 
    closes: List[float], 
    changes: List[float]
) -> Dict:
    """分析量价关系
    
    Args:
        volumes: 成交量列表
        closes: 收盘价列表
        changes: 涨跌幅列表
    
    Returns:
        量价关系分析结果
    """
    if not volumes or not closes or len(volumes) < 2 or len(closes) < 2:
        return {"type": "数据不足", "description": "数据不足"}
    
    # 取最近几天数据分析
    n = min(5, len(volumes))
    recent_volumes = volumes[-n:]
    recent_closes = closes[-n:]
    recent_changes = changes[-n:]
    
    # 计算整体趋势
    price_trend = "上涨" if recent_changes[-1] > 0 else "下跌" if recent_changes[-1] < 0 else "持平"
    volume_trend = "放大" if recent_volumes[-1] > sum(recent_volumes[:-1]) / (n-1) else "缩小"
    
    # 判断量价配合类型
    if n >= 3:
        # 检查是否是量价齐升（价涨量增）
        price_up = recent_changes[-1] > 0
        volume_up = recent_volumes[-1] > sum(recent_volumes[:-1]) / (n-1)
        
        # 检查是否是量价背离（价涨量缩）
        price_up_volume_down = price_up and recent_volumes[-1] < sum(recent_volumes[:-1]) / (n-1)
        
        # 检查是否是放量下跌（跌时放量）
        price_down = recent_changes[-1] < 0
        volume_up_price_down = price_down and volume_up
        
        # 检查是否是缩量下跌（跌时缩量）
        volume_down_price_down = price_down and recent_volumes[-1] < sum(recent_volumes[:-1]) / (n-1)
        
        # 检查是否是地量（成交量极度萎缩）
        min_volume = min(recent_volumes)
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        is_di_liang = min_volume < avg_volume * 0.3
        
        # 检查是否是巨量（成交量异常放大）
        max_volume = max(recent_volumes)
        is_ju_liang = max_volume > avg_volume * 2.5
        
        # 判断当前量价关系类型
        if price_up_volume_down:
            volume_price_type = "量价背离"
            description = "价格上涨但成交量萎缩，需警惕回调风险"
        elif price_up and volume_up:
            volume_price_type = "量价齐升"
            description = "量价配合良好，上涨趋势健康"
        elif volume_up_price_down:
            volume_price_type = "放量下跌"
            description = "下跌时放量，可能预示进一步下跌风险"
        elif volume_down_price_down:
            volume_price_type = "缩量下跌"
            description = "下跌时缩量，抛压减轻，可能接近底部"
        elif is_di_liang:
            volume_price_type = "地量"
            description = "成交量极度萎缩，可能预示变盘节点"
        elif is_ju_liang:
            volume_price_type = "巨量"
            description = "成交量异常放大，需关注后续走势"
        else:
            volume_price_type = "常态波动"
            description = "成交量波动处于正常范围"
    else:
        volume_price_type = "数据不足"
        description = "数据不足，无法准确判断"
    
    return {
        "type": volume_price_type,
        "description": description,
        "price_trend": price_trend,
        "volume_trend": volume_trend
    }


def get_volume_analysis_report(secid: str, days: int = 20) -> str:
    """生成成交量分析报告文本
    
    Args:
        secid: 股票代码标识（如 "1.600036"）
        days: 分析天数
    
    Returns:
        格式化的分析报告文本
    """
    # 获取历史数据
    history = get_kline_data(secid, days)
    if not history:
        return "**成交量分析**：数据获取失败，无法进行分析"
    
    # 获取实时行情中的成交量
    realtime = get_realtime_quote(secid)
    
    # 分析成交量特征
    analysis = analyze_volume特征(history, days)
    
    if not analysis.get("success"):
        return f"**成交量分析**：{analysis.get('error', '分析失败')}"
    
    # 构建分析报告
    report_lines = ["**成交量分析**", ""]
    
    # 获取当前时段信息
    is_am, time_session = is_morning_session()
    
    # 1. 成交量概况
    report_lines.append("### 1. 成交量概况")
    
    # 添加时段说明
    if is_am:
        report_lines.append(f"- ⚠️ **当前为上午盘数据**，仅为半天成交量，最终成交量可能翻倍")
    else:
        report_lines.append(f"- 📊 当前为{'下午盘' if '盘' in time_session else time_session}数据")
    
    current_vol = analysis.get("current_volume_万手", 0)
    avg_vol_5 = analysis.get("avg_volume_5_万手", 0)
    avg_vol_10 = analysis.get("avg_volume_10_万手", 0)
    avg_vol_20 = analysis.get("avg_volume_20_万手", 0)
    
    report_lines.append(f"- 今日成交量：{current_vol:.2f} 万手")
    if avg_vol_5:
        report_lines.append(f"- 5日均量：{avg_vol_5:.2f} 万手")
    if avg_vol_10:
        report_lines.append(f"- 10日均量：{avg_vol_10:.2f} 万手")
    if avg_vol_20:
        report_lines.append(f"- 20日均量：{avg_vol_20:.2f} 万手")
    
    # 2. 成交量变化
    report_lines.append("")
    report_lines.append("### 2. 成交量变化")
    vol_change = analysis.get("volume_change_ratio", 0)
    if vol_change > 0:
        report_lines.append(f"- 成交量较昨日放大：{vol_change:.1f}%")
    elif vol_change < 0:
        report_lines.append(f"- 成交量较昨日缩小：{abs(vol_change):.1f}%")
    else:
        report_lines.append("- 成交量较昨日持平")
    
    if analysis.get("is_volume_up"):
        report_lines.append("- **当前处于放量状态**（高于5日均量50%以上）")
    elif analysis.get("is_volume_down"):
        report_lines.append("- **当前处于缩量状态**（低于5日均量50%以上）")
    
    # 3. 换手率分析
    report_lines.append("")
    report_lines.append("### 3. 换手率分析")
    current_turnover = analysis.get("current_turnover", 0)
    avg_turnover = analysis.get("avg_turnover", 0)
    report_lines.append(f"- 今日换手率：{current_turnover:.2f}%")
    if avg_turnover:
        report_lines.append(f"- 平均换手率：{avg_turnover:.2f}%")
    if current_turnover > avg_turnover * 1.5:
        report_lines.append("- 换手率偏高，交投活跃")
    elif current_turnover < avg_turnover * 0.5:
        report_lines.append("- 换手率偏低，交投清淡")
    
    # 4. 量价关系分析
    report_lines.append("")
    report_lines.append("### 4. 量价关系分析")
    vp_relation = analysis.get("volume_price_relation", {})
    vp_type = vp_relation.get("type", "未知")
    vp_desc = vp_relation.get("description", "")
    price_trend = vp_relation.get("price_trend", "")
    volume_trend = vp_relation.get("volume_trend", "")
    
    report_lines.append(f"- 当前量价关系：**{vp_type}**")
    report_lines.append(f"- 价格趋势：{price_trend}")
    report_lines.append(f"- 成交量趋势：{volume_trend}")
    report_lines.append(f"- 分析：{vp_desc}")
    
    # 5. 综合判断
    report_lines.append("")
    report_lines.append("### 5. 综合判断")
    
    # 根据各项指标给出综合判断
    signals = []
    
    # 上午盘特别提示
    if is_am:
        signals.append("⚠️ 上午盘数据，仅供参考，实际成交量可能翻倍")
    
    if vp_type == "量价齐升":
        signals.append("量价配合健康，涨势可持续")
    elif vp_type == "量价背离":
        signals.append("量价背离，需警惕回调风险")
    elif vp_type == "放量下跌":
        signals.append("下跌放量，需注意风险")
    elif vp_type == "缩量下跌":
        signals.append("缩量下跌，抛压减轻，可能接近底部")
    elif vp_type == "地量":
        signals.append("地量信号，可能迎来变盘")
    elif vp_type == "巨量":
        signals.append("巨量出现，关注后续走势")
    
    if analysis.get("is_volume_up") and price_trend == "上涨":
        signals.append("放量上涨，多头积极")
    elif analysis.get("is_volume_down") and price_trend == "下跌":
        signals.append("缩量下跌，观望为主")
    
    if current_turnover > 10:
        signals.append("换手率较高，交投活跃")
    elif current_turnover < 1:
        signals.append("换手率较低，流动性不足")
    
    for signal in signals:
        report_lines.append(f"- {signal}")
    
    return "\n".join(report_lines)


def get_volume_feature_summary(secid: str, days: int = 20) -> Dict:
    """获取成交量特征摘要（用于AI分析）
    
    Args:
        secid: 股票代码标识
        days: 分析天数
    
    Returns:
        成交量特征摘要字典
    """
    history = get_kline_data(secid, days)
    if not history:
        return {"error": "数据获取失败"}
    
    analysis = analyze_volume特征(history, days)
    
    if not analysis.get("success"):
        return {"error": analysis.get("error", "分析失败")}
    
    vp_relation = analysis.get("volume_price_relation", {})
    
    # 构建摘要
    summary = {
        "今日成交量_万手": round(analysis.get("current_volume_万手", 0), 2),
        "5日均量_万手": round(analysis.get("avg_volume_5_万手", 0), 2) if analysis.get("avg_volume_5_万手") else None,
        "10日均量_万手": round(analysis.get("avg_volume_10_万手", 0), 2) if analysis.get("avg_volume_10_万手") else None,
        "成交量变化": f"{analysis.get('volume_change_ratio', 0):.1f}%",
        "成交量状态": "放量" if analysis.get("is_volume_up") else "缩量" if analysis.get("is_volume_down") else "正常",
        "今日换手率": f"{analysis.get('current_turnover', 0):.2f}%",
        "平均换手率": f"{analysis.get('avg_turnover', 0):.2f}%" if analysis.get("avg_turnover") else None,
        "量价关系类型": vp_relation.get("type", "未知"),
        "量价关系描述": vp_relation.get("description", ""),
        "价格趋势": vp_relation.get("price_trend", ""),
    }
    
    return summary


if __name__ == "__main__":
    # 测试代码
    import json
    
    # 测试获取成交量分析报告
    print("=== 测试成交量分析报告 ===")
    secid = "1.600036"  # 招商银行
    report = get_volume_analysis_report(secid, days=20)
    print(report)
    
    print("\n=== 测试成交量特征摘要 ===")
    summary = get_volume_feature_summary(secid, days=20)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
