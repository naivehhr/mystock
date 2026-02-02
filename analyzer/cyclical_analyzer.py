# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import base64
import io
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

def generate_cyclical_chart_base64(industries_data):
    """为每个行业生成独立的周期位置图表并返回Base64编码"""
    try:
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 为每个行业生成单独的图表
        base64_images = []
        for i, industry in enumerate(industries_data):
            fig, ax = plt.subplots(figsize=(6, 4))
            
            # 定义周期阶段和位置
            phases = ["底部", "复苏", "上升", "顶部", "回落"]
            phase_positions = [0, 0.25, 0.5, 0.75, 1.0]
            
            # 解析周期位置百分比，用于精确定位
            cycle_position_str = industry.get('cycle_position', '')
            current_phase = industry['current_phase']
            
            # 尝试从 cycle_position 解析百分比（如"上升期第62%"）
            percentage_match = re.search(r'(\d+)%', cycle_position_str)
            if percentage_match:
                # 使用解析的百分比作为 X 坐标（0-1 范围）
                pos = int(percentage_match.group(1)) / 100.0
            else:
                # 回退：根据 current_phase 关键词映射
                if "底部" in current_phase or "下行" in current_phase or "衰退" in current_phase:
                    pos = 0.1
                elif "复苏" in current_phase or "启动" in current_phase:
                    pos = 0.25
                elif "上升" in current_phase or "成长" in current_phase:
                    pos = 0.5
                elif "顶部" in current_phase or "见顶" in current_phase or "高位" in current_phase:
                    pos = 0.8
                elif "回落" in current_phase or "调整" in current_phase or "政策驱动" in current_phase:
                    pos = 0.6
                else:
                    pos = 0.3
            
            # 绘制周期曲线
            # 使用完整正弦波周期：底部(0)->复苏(0.25)->顶部(0.5)->回落(0.75)->底部(1.0)
            x_curve = np.linspace(0, 1, 100)
            y_curve = 0.5 * np.sin(2 * np.pi * x_curve - np.pi/2) + 0.5
            ax.plot(x_curve, y_curve, '--', linewidth=1.5, color='gray', alpha=0.6, label='理论周期曲线')
            
            # 计算行业位置点在曲线上的 Y 坐标
            y_pos = 0.5 * np.sin(2 * np.pi * pos - np.pi/2) + 0.5
            
            # 绘制行业位置点
            ax.scatter(pos, y_pos, s=100, alpha=0.8, color='red', zorder=5)
            ax.annotate(industry['industry'], 
                       xy=(pos, y_pos), 
                       xytext=(0, 12), 
                       textcoords='offset points',
                       ha='center', va='bottom',
                       fontsize=10, fontweight='bold', color='red')
            
            # 设置X轴和Y轴标签
            ax.set_xticks(phase_positions)
            ax.set_xticklabels(phases, rotation=0, ha='center', fontsize=9)
            ax.set_xlim(-0.1, 1.1)
            ax.set_ylim(-0.05, 1.05)
            ax.set_xlabel('经济周期阶段', fontsize=10, labelpad=5)
            ax.set_ylabel('行业景气度位置', fontsize=10, labelpad=5)
            ax.set_title(f'{industry["industry"]}行业周期位置分析', fontsize=11, fontweight='bold', pad=10)
            ax.grid(True, alpha=0.3)
            
            # 添加垂直参考线
            for phase_pos, phase_label in zip(phase_positions, phases):
                ax.axvline(x=phase_pos, color='lightgray', linestyle=':', alpha=0.7)
            
            plt.tight_layout()
            
            # 将图像保存到内存中的字节流
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
            img_buffer.seek(0)
            
            # 将图像转换为base64编码
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            plt.close()
            
            base64_images.append(img_base64)
        
        return base64_images
    except Exception as e:
        print(f"生成周期性行业图表失败: {e}")
        return None

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
        
        # 4. 生成图表
        base64_charts = generate_cyclical_chart_base64(industries_data)
        
        if base64_charts and len(base64_charts) == len(industries_data):
            for i, industry in enumerate(industries_data):
                industry['chart_base64'] = base64_charts[i]
        
        return industries_data
    except Exception as e:
        print(f"分析周期性行业失败: {e}")
        return None
