# -*- coding: utf-8 -*-
"""
配置管理器
处理配置加载，优先级：config.py > 环境变量 > 默认值
"""

import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        # 尝试导入配置文件
        self.config = {}
        config_file = Path(__file__).parent / "config.py"
        
        if config_file.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", config_file)
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                # 从配置文件获取值
                self.config['EMAIL_SENDER'] = getattr(config_module, 'EMAIL_SENDER', '')
                self.config['EMAIL_AUTH_CODE'] = getattr(config_module, 'EMAIL_AUTH_CODE', '')
                self.config['EMAIL_RECEIVER'] = getattr(config_module, 'EMAIL_RECEIVER', '')
                self.config['HEADERS'] = getattr(config_module, 'HEADERS', {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://quote.eastmoney.com/",
                })
                self.config['REPORTS_DIR'] = getattr(config_module, 'REPORTS_DIR', '')
                self.config['CYCLICAL_INDUSTRIES'] = getattr(config_module, 'CYCLICAL_INDUSTRIES', ['军工'])
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                # 如果加载失败，使用默认值
                self._set_defaults()
        else:
            # 如果配置文件不存在，则使用默认值和环境变量
            self._set_defaults()
    
    def _set_defaults(self):
        """设置默认值，优先使用环境变量"""
        self.config['EMAIL_SENDER'] = os.getenv('EMAIL_SENDER', '')
        self.config['EMAIL_AUTH_CODE'] = os.getenv('EMAIL_AUTH_CODE', '')
        self.config['EMAIL_RECEIVER'] = os.getenv('EMAIL_RECEIVER', '')
        self.config['HEADERS'] = {
            "User-Agent": os.getenv('USER_AGENT', "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            "Referer": os.getenv('REFERER', "https://quote.eastmoney.com/"),
        }
        self.config['REPORTS_DIR'] = os.getenv('REPORTS_DIR', '')
        self.config['CYCLICAL_INDUSTRIES'] = os.getenv('CYCLICAL_INDUSTRIES', '军工').split(',')
    
    @property
    def email_sender(self):
        return self.config['EMAIL_SENDER']
    
    @property
    def email_auth_code(self):
        return self.config['EMAIL_AUTH_CODE']
    
    @property
    def email_receiver(self):
        return self.config['EMAIL_RECEIVER']
    
    @property
    def headers(self):
        return self.config['HEADERS']
    
    @property
    def reports_dir(self):
        # 如果配置中没有指定报告目录，则使用默认值
        if self.config['REPORTS_DIR']:
            return Path(self.config['REPORTS_DIR'])
        else:
            return Path.home() / "stock-reports" / "reports"
    
    @property
    def cyclical_industries(self):
        return self.config['CYCLICAL_INDUSTRIES']

# 创建全局配置实例
config = ConfigManager()