# -*- coding: utf-8 -*-
import re
from config_manager import config
from ai_analyzer import ai_analyze_cyclical_industry
from data_fetcher import get_realtime_quote

# 行业与代码映射 (东方财富 secid)
INDUSTRY_MAP = {
    "军工": "90.BK0424",
    "猪肉": "90.BK0574",
    "半导体": "90.BK0917",
    "光伏": "90.BK0822",
    "新能源车": "90.BK0900",
}

# 行业周期分析禁用图表形式，仅支持文字和表格输出

def analyze_cyclical_industries():
    """分析周期性行业（支持配置，默认军工）"""
    try:
        industry_names = config.cyclical_industries
        industries_data = []
        
        for name in industry_names:
            print(f"正在分析周期性行业: {name}...")
            
            # 1. 尝试获取真实数据
            secid = INDUSTRY_MAP.get(name)
            real_data = None
            if secid:
                real_data = get_realtime_quote(secid)
            
            # 2. 调用 AI 进行周期分析
            ai_result = ai_analyze_cyclical_industry(name, real_data)
            print(f"--- AI 周期分析结果 ({name}) ---\n{ai_result}\n")
            
            # 3. 解析 AI 结果
            analysis_dict = {
                "industry": name,
                "current_phase": "未知",
                "cycle_position": "未知",
                "duration": "未知",
                "analysis": ai_result
            }
            
            # 尝试结构化解析 AI 返回的固定格式（支持带 markdown 格式的情况）
            if ai_result and "当前周期" in ai_result:
                lines = ai_result.split("\n")
                for line in lines:
                    # 移除 markdown 格式标记
                    clean_line = line.replace("**", "").strip()
                    if clean_line.startswith("当前周期:"):
                        analysis_dict["current_phase"] = clean_line.replace("当前周期:", "").strip()
                    elif clean_line.startswith("周期位置:"):
                        analysis_dict["cycle_position"] = clean_line.replace("周期位置:", "").strip()
                    elif clean_line.startswith("持续时间:"):
                        analysis_dict["duration"] = clean_line.replace("持续时间:", "").strip()
                    elif clean_line.startswith("分析:"):
                        analysis_dict["analysis"] = clean_line.replace("分析:", "").strip()
            
            industries_data.append(analysis_dict)
        
        # 4. 不生成图表（根据用户偏好禁用图表形式）
        
        return industries_data
    except Exception as e:
        print(f"分析周期性行业失败: {e}")
        return None
