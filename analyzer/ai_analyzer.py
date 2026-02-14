# -*- coding: utf-8 -*-
import subprocess
import re


def call_ai(prompt):
    """调用 AI CLI 执行分析"""
    # Qoder CLI 路径
    qodercli_path = "/Applications/Qoder.app/Contents/Resources/app/resources/bin/aarch64_darwin/qodercli"

    try:
        # 使用 qodercli 进行分析
        result = subprocess.run(
            [qodercli_path, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode == 0:
            response = result.stdout.strip()
            # 检查返回内容是否为拒绝回答
            refuse_patterns = [
                r"我是Qoder.*软件工程",
                r"无法提供.*投资建议",
                r"没有.*金融.*能力",
                r"不属于.*专业范围"
            ]
            for pattern in refuse_patterns:
                if re.search(pattern, response):
                    # Qoder拒绝回答，使用规则模板
                    return None
            return response
        else:
            return f"*AI 分析调用失败: {result.stderr}*"
    except FileNotFoundError:
        return "*Qoder CLI 未找到，跳过 AI 分析*"
    except subprocess.TimeoutExpired:
        return "*AI 分析超时*"
    except Exception as e:
        return f"*AI 分析出错: {e}*"


def generate_rule_based_analysis(name, data):
    """基于规则生成简单分析（当AI不可用时使用）"""
    # 提取关键数据
    analysis_parts = []
    
    # 尝试从数据中提取涨跌幅信息
    change_pattern = r'涨跌幅[:：]\s*([-\d.]+)%'
    matches = re.findall(change_pattern, data)
    
    # 尝试提取主力资金流向
    flow_pattern = r'主力净流入[:：]\s*([-\d.]+)'
    flow_matches = re.findall(flow_pattern, data)
    
    # 生成分析
    if name == "沪深300":
        analysis_parts.append(f"**{name}市场分析**：")
        if matches:
            try:
                change = float(matches[0])
                if change < 0:
                    analysis_parts.append(f"今日下跌{abs(change):.2f}%，")
                else:
                    analysis_parts.append(f"今日上涨{change:.2f}%，")
            except:
                pass
        analysis_parts.append("市场整体表现较为震荡。")
        if flow_matches:
            try:
                total_flow = sum(float(f) for f in flow_matches[:3]) / 100000000
                if total_flow < 0:
                    analysis_parts.append(f"近期主力资金呈净流出状态，累计约{total_flow:.0f}亿元。")
                else:
                    analysis_parts.append(f"近期主力资金呈净流入状态。")
            except:
                pass
    elif "白酒" in name:
        analysis_parts.append(f"**{name}分析**：")
        if matches:
            try:
                change = float(matches[0])
                if change < 0:
                    analysis_parts.append(f"近期下跌{abs(change):.2f}%，")
                else:
                    analysis_parts.append(f"近期上涨{change:.2f}%，")
            except:
                pass
        analysis_parts.append("建议关注消费板块政策和行业基本面变化。")
    elif "银行" in name:
        analysis_parts.append(f"**{name}分析**：")
        if matches:
            try:
                change = float(matches[0])
                if change < 0:
                    analysis_parts.append(f"近期回调{abs(change):.2f}%，")
                else:
                    analysis_parts.append(f"近期上涨{change:.2f}%，")
            except:
                pass
        if flow_matches:
            try:
                total_flow = sum(float(f) for f in flow_matches[:3]) / 100000000
                if total_flow < 0:
                    analysis_parts.append(f"主力资金净流出约{abs(total_flow):.0f}亿元，需关注资金面变化。")
            except:
                pass
    else:
        analysis_parts.append(f"**{name}简析**：")
        if matches:
            analysis_parts.append("关注近期走势和资金流向。")
    
    # 添加风险提示
    analysis_parts.append("\n*注：此分析基于规则模板生成，仅供参考，投资需谨慎。*")
    
    return "".join(analysis_parts)


def ai_analyze_target(name, data):
    """为单个标的调用 AI 进行分析"""
    prompt = f"""你是我的资本市场分析助手，拥有丰富的炒股实战经验，尤其对A股市场风格有深刻的理解。请基于以下 {name} 的市场数据，给出专业的投资分析和可落地的实施方案建议：

{data}

分析要求：
1. 简述近期走势（根据3天行情判断）
2. 解读主力资金动向
3. 结合A股市场特点，给出具体可操作的实施方案建议

请用中文回答，保持客观专业，控制在200字以内。"""
    result = call_ai(prompt)
    # 如果AI返回None（拒绝回答），使用规则模板
    if result is None:
        return generate_rule_based_analysis(name, data)
    return result


def ai_analyze_summary(full_content):
    """为全市场和多标的关联调用 AI 进行综合总结"""
    prompt = f"""请基于以下多标的分析数据，进行一个简短的市场综合总结：
    
{full_content}

总结要求：
1. 概括当前整体市场情绪（结合各标的表现）
2. 提醒潜在的系统性风险或机会

请用中文回答，专业干练，控制在150字以内。"""
    result = call_ai(prompt)
    # 如果AI返回None（拒绝回答），使用规则模板生成简单总结
    if result is None:
        return generate_summary_from_content(full_content)
    return result


def generate_summary_from_content(content):
    """基于内容生成简单总结（当AI不可用时使用）"""
    summary_parts = []
    
    # 提取涨跌幅信息
    change_pattern = r'涨跌幅[:：]\s*([-\d.]+)%'
    changes = re.findall(change_pattern, content)
    
    # 统计涨跌
    up_count = sum(1 for c in changes if float(c) > 0)
    down_count = sum(1 for c in changes if float(c) < 0)
    
    if up_count > down_count:
        summary_parts.append("今日市场整体偏暖，")
    elif down_count > up_count:
        summary_parts.append("今日市场整体承压，")
    else:
        summary_parts.append("今日市场表现分化，")
    
    # 提取资金流向
    flow_pattern = r'主力净流入[:：]\s*([-\d.]+)'
    flows = re.findall(flow_pattern, content)
    if flows:
        try:
            total = sum(float(f) for f in flows[:5]) / 100000000
            if total < 0:
                summary_parts.append(f"主力资金净流出约{abs(total):.0f}亿元。")
            else:
                summary_parts.append(f"主力资金呈净流入状态。")
        except:
            pass
    
    # 添加风险提示
    summary_parts.append("建议关注政策面和资金面变化，控制仓位，谨慎操作。")
    summary_parts.append("\n*注：此总结基于规则模板生成，仅供参考。*")
    
    return "".join(summary_parts)


def ai_analyze_cyclical_industry(industry_name, industry_data=None):
    """为周期性行业调用 AI 进行周期阶段分析"""
    data_str = f"实时行情数据: {industry_data}" if industry_data else "暂无实时数据，请根据你的知识储备进行分析。"

    prompt = f"""你是专业的行业研究员。请对 {industry_name} 行业进行周期性分析。
    
{data_str}

分析要求：
1. **当前周期**: 简洁描述（如：下行周期底部区域、政策驱动上升期等）
2. **周期位置**: 4-6个字（如：底部向上拐点、稳步上升等）
3. **持续时间**: 预估当前阶段已持续或将持续的时间
4. **深度分析**: 100字以内的专业行业逻辑分析

请严格按照以下格式回答，不要有任何多余文字：
当前周期: [内容]
周期位置: [内容]
持续时间: [内容]
分析: [内容]"""
    return call_ai(prompt)
