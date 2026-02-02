#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深300 股票分析脚本 - 重构版
- 数据来源：东方财富 API
- 模块化拆分：data_fetcher, ai_analyzer, cyclical_analyzer, notifier, report_generator
"""

import sys
from datetime import datetime

# 强制 stdout 无缓冲输出，确保日志实时写入文件
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
from ai_analyzer import ai_analyze_target, ai_analyze_summary
from data_fetcher import is_trading_day
from report_generator import (
    generate_target_report, 
    generate_sector_report, 
    generate_cyclical_industry_report, 
    save_report
)
from notifier import send_email

# 配置
TARGETS = [
    {"code": "000300", "name": "沪深300", "secid": "1.000300", "type": "index"},
    {"code": "161725", "name": "招商中证白酒指数", "secid": "0.161725", "type": "fund"},
    {"code": "600036", "name": "招商银行", "secid": "1.600036", "type": "stock"},
]

def main():
    # 检查是否为交易日
    if not is_trading_day():
        print(f"[{datetime.now()}] 今日为非交易日，跳过执行。")
        return
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now()}] 开始生成多标的分析报告...")
    print("数据来源: 东方财富")
    
    full_report_parts = [
        f"# 股票/基金智能分析报告 - {today_str}",
        "",
        "---",
        ""
    ]
    
    # 1. 遍历标的生成报告（包含单标的 AI 分析）
    has_any_valid_data = False
    
    for target in TARGETS:
        name = target['name']
        print(f"正在获取 {name} ({target['code']}) 数据并进行 AI 分析...")
        target_report, status = generate_target_report(target)
        
        # 单标的 AI 分析
        if status["history"] or status["money_flow"]:
            has_any_valid_data = True
            target_ai = ai_analyze_target(name, target_report)
        else:
            target_ai = "*因数据获取失败，无法进行 AI 分析*"
            
        # print(f"--- AI 分析结果 ({name}) ---\n{target_ai}\n")
            
        full_report_parts.append(target_report)
        full_report_parts.append(f"### AI 智能研判 ({name})")
        full_report_parts.append(target_ai)
        full_report_parts.append("")
        full_report_parts.append("---")
    
    # 2. 添加热门板块分析
    print("正在获取热门板块数据...")
    sector_report = generate_sector_report()
    full_report_parts.append(sector_report)
    
    # 3. 添加周期性行业分析
    print("正在分析周期性行业...")
    cyclical_report = generate_cyclical_industry_report()
    full_report_parts.append(cyclical_report)
    
    # 4. 综合总结 AI 分析
    if has_any_valid_data:
        print("正在进行市场综合总结...")
        full_data_content = "\n".join(full_report_parts)
        summary_ai = ai_analyze_summary(full_data_content)
        print(f"--- 市场综合总结 ---\n{summary_ai}\n")
    else:
        summary_ai = "*因数据获取失败，无法进行综合总结*"
    
    full_report_parts.append("## 五、市场综合总结")
    full_report_parts.append(summary_ai)
    
    # 5. 合并最终报告
    full_report = (
        "\n".join(full_report_parts) + 
        "\n\n---\n*数据来源: 东方财富 | 报告生成时间: " + 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*\n"
    )
    
    # 6. 保存报告
    filepath = save_report(full_report)
    print(f"报告已保存: {filepath}")
    
    # 7. 发送邮件
    subject = f"股票/基金智能分析报告 - {today_str}"
    send_email(subject, full_report)
    
    return filepath

if __name__ == "__main__":
    main()
