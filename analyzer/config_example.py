# -*- coding: utf-8 -*-
"""
示例配置文件
注意：这是一个示例文件，请勿直接使用真实信息
如需使用，请复制此文件为 config.py 并填入实际值，然后确保 config.py 不会被提交到版本控制系统
"""

# 邮件配置
EMAIL_SENDER = "your_email@domain.com"  # 你的发件邮箱
EMAIL_AUTH_CODE = "your_app_password_or_auth_code"  # 你的邮箱授权码/应用密码
EMAIL_RECEIVER = "recipient@domain.com"  # 你的收件邮箱

# 东方财富 API Headers (如有需要可自定义)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

# 其他配置
REPORTS_DIR = "/path/to/your/reports"  # 报告目录路径，留空则使用默认值 (~/.stock-reports/reports)
CYCLICAL_INDUSTRIES = ["军工"]  # 周期性行业列表，目前仅支持 军工，后续可扩展