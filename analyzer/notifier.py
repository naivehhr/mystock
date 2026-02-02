# -*- coding: utf-8 -*-
import smtplib
import sys
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from config_manager import config

try:
    import markdown
except ImportError:
    print("请先安装依赖: pip install markdown")
    sys.exit(1)

# 邮件配置
EMAIL_SENDER = config.email_sender
EMAIL_AUTH_CODE = config.email_auth_code
EMAIL_RECEIVER = config.email_receiver
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465

def send_email(subject, content):
    """发送邮件报告（优化的HTML格式）"""
    if not EMAIL_SENDER or not EMAIL_AUTH_CODE or not EMAIL_RECEIVER:
        print("邮件配置不完整，跳过邮件发送。请检查配置文件或环境变量。")
        return False
    
    print(f"正在发送邮件报告至 {EMAIL_RECEIVER}...")
    try:
        # 将 Markdown 转换为 HTML，支持表格扩展
        html_body = markdown.markdown(content, extensions=['tables'])
        
        # 内联CSS样式
        styled_content = html_body.replace(
            '<table>',
            '<table style="border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; min-width: 600px;">'
        ).replace(
            '<th>',
            '<th style="border: 1px solid #ddd; padding: 12px 10px; text-align: center; background-color: #f8f9fa; color: #2c3e50; font-weight: bold;">'
        ).replace(
            '<td>',
            '<td style="border: 1px solid #ddd; padding: 12px 10px; text-align: center;">'
        ).replace(
            '<tr>',
            '<tr style="background-color: #fff;">'
        )
        
        # 高亮今日行情数据行 (背景浅黄色)
        styled_content = re.sub(
            r'<tr style="background-color: #fff;">(\s*<td[^>]*>\[TODAY\])',
            r'<tr style="background-color: #fff9c4;">\1',
            styled_content
        )
        # 移除 [TODAY] 标记
        styled_content = styled_content.replace('[TODAY]', '')

        styled_content = styled_content.replace(
            '<h1>',
            '<h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; font-size: 24px; text-align: center; margin-top: 0;">'
        ).replace(
            '<h2>',
            '<h2 style="color: #2980b9; border-left: 5px solid #3498db; padding-left: 15px; margin-top: 35px; font-size: 20px; background-color: #f8f9fa; padding-top: 10px; padding-bottom: 10px;">'
        ).replace(
            '<h3>',
            '<h3 style="color: #16a085; margin-top: 25px; font-size: 18px; border-bottom: 1px solid #eee; padding-bottom: 5px;">'
        ).replace(
            '<strong>',
            '<strong style="color: #e74c3c;">'
        ).replace(
            '<hr>',
            '<hr style="border: 0; border-top: 1px solid #eee; margin: 40px 0;">'
        ).replace(
            '<blockquote>',
            '<blockquote style="margin: 20px 0; padding: 15px 20px; background-color: #f0f7ff; border-left: 5px solid #3498db; color: #34495e; border-radius: 4px;">'
        )
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f5f5f5;">
                <tr>
                    <td style="padding: 20px 0;">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" width="90%" style="max-width: 900px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <tr>
                                <td style="padding: 30px;">
                                    <div style="color: #333;">
                                        {styled_content}
                                    </div>
                                    <div style="text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999;">
                                        <p>本报告由 Qoder AI 自动生成 | 数据来源：东方财富</p>
                                        <p>© {datetime.now().year} 股票/基金智能研判系统</p>
                                    </div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = formataddr(("市场分析助手", EMAIL_SENDER))
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.attach(MIMEText(full_html, 'html', 'utf-8'))
        
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_SENDER, EMAIL_AUTH_CODE)
            server.send_message(msg)
            
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False
