# -*- coding: utf-8 -*-
from datetime import datetime
from config_manager import config
from data_fetcher import get_realtime_quote, get_index_history, get_money_flow, get_sector_data, get_chip_distribution, get_stock_chip_image_and_data
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
    
    # K 线走势图
    report_lines.append("### 日 K 线走势图")
    # 根据 secid 前缀判断市场代码：1=sh(上证), 0=sz(深证)
    market_prefix = secid.split('.')[0]
    market_code = "sh" if market_prefix == "1" else "sz"
    stock_code = target['code']
    kline_url = f"http://image.sinajs.cn/newchart/daily/n/{market_code}{stock_code}.gif"
    report_lines.append(f"![{name}日 K]({kline_url})")
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
    
    # 3. 筹码分布（仅个股显示）
    # 只有个股才获取筹码分布图和详细数据
    chip_image_base64 = None
    chip_detail_data = None
    chip_data = None  # 初始化变量
    
    if target['type'] == 'stock':
        report_lines.append("### 筹码分布")
        
        print(f"\n--- 开始获取 {name} ({target['code']}) 的筹码分布信息 ---")
        try:
            chip_image_base64, chip_detail_data = get_stock_chip_image_and_data(target['code'])
            
            if chip_image_base64:
                print(f"成功获取 {name} 的筹码分布图")
                report_lines.append(f'<img src="data:image/png;base64,{chip_image_base64}" alt="{name}筹码分布" style="max-width:100%; height:auto; border:1px solid #ddd; border-radius:4px;">')
                report_lines.append("")
            else:
                print(f"未能获取 {name} 的筹码分布图")
            
            # 显示筹码分布详细数据
            if chip_detail_data:
                print(f"成功获取 {name} 的筹码分布数据")
                report_lines.append("**筹码分布详情**")
                report_lines.append("")
                
                if '日期' in chip_detail_data:
                    report_lines.append(f"- **数据日期**: {chip_detail_data['日期']}")
                if '获利比例' in chip_detail_data:
                    report_lines.append(f"- **获利比例**: {chip_detail_data['获利比例']}")
                if '平均成本' in chip_detail_data:
                    report_lines.append(f"- **平均成本**: {chip_detail_data['平均成本']}")
                if '90%成本' in chip_detail_data:
                    report_lines.append(f"- **90%成本区间**: {chip_detail_data['90%成本']}")
                if '90%集中度' in chip_detail_data:
                    report_lines.append(f"- **90%集中度**: {chip_detail_data['90%集中度']}")
                if '70%成本' in chip_detail_data:
                    report_lines.append(f"- **70%成本区间**: {chip_detail_data['70%成本']}")
                if '70%集中度' in chip_detail_data:
                    report_lines.append(f"- **70%集中度**: {chip_detail_data['70%集中度']}")
                
                report_lines.append("")
            else:
                print(f"未能获取 {name} 的筹码分布数据")
                
        except Exception as e:
            print(f"获取 {name} 筹码分布信息错误: {e}")
            import traceback
            traceback.print_exc()
        print(f"--- 筹码分布信息获取结束 ---\n")
    
    report_lines.append("")
    
    # 4. 恒生科技指数特别分析（如果配置了 HSTECH）
    if target.get('is_hstech', False):
        from hstech_analyzer import HSTECHAnalyzerFacade
        
        report_lines.append("### 恒生科技指数智能分析")
        print(f"\n--- 开始生成 {name} 智能分析报告 ---")
        
        try:
            analyzer = HSTECHAnalyzerFacade()
            report = analyzer.generate_full_report(save_chart=True, verbose=False)
            
            if report:
                # 添加文字分析
                report_lines.append("**智能分析结果**")
                report_lines.append("")
                report_lines.append(report["llm_analysis"])
                report_lines.append("")
                
                # 添加 Base64 图表（带滚动容器）
                if report.get("chart_base64"):
                    print(f"成功获取 {name} 的分析图表（Base64）")
                    # 使用滚动容器包裹图片，支持横向滑动
                    report_lines.append(f'<img src="data:image/png;base64,{report["chart_base64"]}" alt="{name}技术分析图" style="display: block; width: 100px; min-width: 100%; height: auto;">')
                else:
                    print(f"未能获取 {name} 的分析图表 Base64 数据")
            else:
                print(f"恒生科技指数分析失败")
                
        except Exception as e:
            print(f"恒生科技指数分析错误：{e}")
            import traceback
            traceback.print_exc()
        print(f"--- 智能分析报告生成结束 ---\n")
    
    report_lines.append("")
    
    return "\n".join(report_lines), {"history": history, "money_flow": money_flow, "chip_distribution": chip_data}

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
