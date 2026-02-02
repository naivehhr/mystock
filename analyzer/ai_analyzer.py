# -*- coding: utf-8 -*-
import subprocess

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
            return result.stdout.strip()
        else:
            return f"*AI 分析调用失败: {result.stderr}*"
    except FileNotFoundError:
        return "*Qoder CLI 未找到，跳过 AI 分析*"
    except subprocess.TimeoutExpired:
        return "*AI 分析超时*"
    except Exception as e:
        return f"*AI 分析出错: {e}*"

def ai_analyze_target(name, data):
    """为单个标的调用 AI 进行分析"""
    prompt = f"""你是我的资本市场分析助手，拥有丰富的炒股实战经验，尤其对A股市场风格有深刻的理解。请基于以下 {name} 的市场数据，给出专业的投资分析和可落地的实施方案建议：

{data}

分析要求：
1. 简述近期走势（根据3天行情判断）
2. 解读主力资金动向
3. 结合A股市场特点，给出具体可操作的实施方案建议

请用中文回答，保持客观专业，控制在200字以内。"""
    return call_ai(prompt)

def ai_analyze_summary(full_content):
    """为全市场和多标的关联调用 AI 进行综合总结"""
    prompt = f"""请基于以下多标的分析数据，进行一个简短的市场综合总结：
    
{full_content}

总结要求：
1. 概括当前整体市场情绪（结合各标的表现）
2. 提醒潜在的系统性风险或机会

请用中文回答，专业干练，控制在150字以内。"""
    return call_ai(prompt)

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
