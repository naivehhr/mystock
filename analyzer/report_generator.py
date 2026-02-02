# -*- coding: utf-8 -*-
from datetime import datetime
from config_manager import config
from data_fetcher import get_realtime_quote, get_index_history, get_money_flow, get_sector_data
from cyclical_analyzer import analyze_cyclical_industries

# 配置
REPORTS_DIR = config.reports_dir

def generate_target_report(target):
    """生成单个标的的报告内容"""
    secid = target["secid"]
    name = target["name"]
    
    report_lines = [
        f"## [{name} ({target['code']})] 分析模块",
        ""
    ]
    
    # 0. 实时行情
    report_lines.append("### 实时行情")
    realtime = get_realtime_quote(secid)
    if realtime:
        report_lines.append(f"- **最新价**: {realtime['最新价']:.2f}")
        report_lines.append(f"- **涨跌幅**: {realtime['涨跌幅']:.2f}%")
        report_lines.append(f"- **涨跌额**: {realtime['涨跌额']:.2f}")
        report_lines.append(f"- **成交额**: {realtime['成交额'] / 100000000:.2f} 亿")
    else:
        report_lines.append("*实时行情获取失败*")
    report_lines.append("")
    
    # 1. 行情数据
    report_lines.append("### 行情数据（最近3天）")
    history = get_index_history(secid, 3)
    if history:
        # 按日期倒排
        history.sort(key=lambda x: x['日期'], reverse=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        report_lines.append("| 日期 | 收盘价 | 涨跌幅 | 成交额(亿) | 振幅 |")
        report_lines.append("|------|--------|--------|------------|------|")
        for row in history:
            amount = row['成交额'] / 100000000
            date_str = row['日期']
            # 如果是今天，添加高亮标记
            if date_str == today_str:
                date_str = f"[TODAY]{date_str}"
                
            report_lines.append(
                f"| {date_str} | {row['收盘']:.2f} | {row['涨跌幅']:.2f}% | {amount:.2f} | {row['振幅']:.2f}% |"
            )
    else:
        report_lines.append("*行情数据获取失败*")
    report_lines.append("")
    
    # 2. 资金流向
    report_lines.append("### 资金流向（最近3天）")
    money_flow = get_money_flow(secid, 3)
    if money_flow:
        # 按日期倒排
        money_flow.sort(key=lambda x: x['日期'], reverse=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        report_lines.append("| 日期 | 主力净流入(亿) | 超大单(亿) | 大单(亿) |")
        report_lines.append("|------|----------------|------------|----------|")
        for row in money_flow:
            date_str = row['日期']
            # 如果是今天，添加高亮标记
            if date_str == today_str:
                date_str = f"[TODAY]{date_str}"
                
            report_lines.append(
                f"| {date_str} | {row['主力净流入']/100000000:.2f} | "
                f"{row['超大单净流入']/100000000:.2f} | {row['大单净流入']/100000000:.2f} |"
            )
    else:
        report_lines.append("*资金流向获取失败*")
    report_lines.append("")
    
    return "\n".join(report_lines), {"history": history, "money_flow": money_flow}

def generate_sector_report():
    """生成热门板块报告内容"""
    report_lines = [
        "## 热门板块分析",
        ""
    ]
    
    sectors = get_sector_data()
    if sectors:
        print(f"获取到 {len(sectors)} 个热门板块数据")
        report_lines.append("### 当前热门板块 TOP 5")
        report_lines.append("| 板块名称 | 涨跌幅 | 资金净流入(亿) |")
        report_lines.append("|---------|--------|-------------|")
        for sector in sectors:
            report_lines.append(
                f"| {sector['name']} | {sector['change_percent']:.2f}% | {sector['net_flow']:.2f} |"
            )
    else:
        report_lines.append("*热门板块数据获取失败*")
    report_lines.append("")
    
    return "\n".join(report_lines)

def generate_cyclical_industry_report():
    """生成周期性行业报告内容"""
    report_lines = [
        "## 周期性行业分析",
        ""
    ]
    
    industries = analyze_cyclical_industries()
    if industries and len(industries) > 0:
        for industry in industries:
            report_lines.append(f"### {industry['industry']} 行业")
            
            chart_base64 = industry.get('chart_base64', None)
            if chart_base64:
                report_lines.append(f'<img src="data:image/png;base64,{chart_base64}" alt="{industry["industry"]}行业周期位置图" width="400" height="250">')
                report_lines.append("")
            
            report_lines.append(f"- **当前周期**: {industry['current_phase']}")
            if 'duration' in industry:
                report_lines.append(f"- **持续时间**: {industry['duration']}")
            if 'cycle_position' in industry:
                report_lines.append(f"- **周期位置**: {industry['cycle_position']}")
            report_lines.append(f"- **分析**: {industry['analysis']}")
            report_lines.append("")
    else:
        report_lines.append("*周期性行业分析失败*")
    report_lines.append("")
    
    return "\n".join(report_lines)

def save_report(content, filename=None):
    """保存报告到文件"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}_多标的分析报告.md"
    
    filepath = REPORTS_DIR / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath
