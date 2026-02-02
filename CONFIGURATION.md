# 配置说明

本项目使用外部配置文件管理敏感信息，以确保安全性。请按照以下步骤进行配置。

## 配置方法

### 方法一：配置文件（推荐）

1. 复制配置模板：
   ```bash
   cp analyzer/config_template.py analyzer/config.py
   ```
   
   或者参考示例配置：
   ```bash
   cp analyzer/config_example.py analyzer/config.py
   ```

2. 编辑 `analyzer/config.py` 文件，填入您的配置信息：
   ```python
   # 邮件配置
   EMAIL_SENDER = "your_email@domain.com"      # 发件人邮箱
   EMAIL_AUTH_CODE = "your_auth_code"          # 邮箱授权码
   EMAIL_RECEIVER = "receiver@domain.com"      # 收件人邮箱
   
   # 可选配置
   REPORTS_DIR = "/path/to/reports"            # 报告保存目录
   ```

### 方法二：环境变量

您也可以通过设置环境变量来配置应用：

```bash
export EMAIL_SENDER="your_email@domain.com"
export EMAIL_AUTH_CODE="your_auth_code"
export EMAIL_RECEIVER="receiver@domain.com"
export REPORTS_DIR="/path/to/reports"
```

## 配置优先级

配置的加载顺序如下（优先级从高到低）：
1. `config.py` 文件
2. 环境变量
3. 默认值

## 邮箱授权码获取

不同邮箱服务提供商获取授权码的方式不同：

- **网易邮箱（163.com）**：登录网页版邮箱 -> 设置 -> POP3/SMTP/IMAP -> 开启服务 -> 获取授权码
- **QQ邮箱**：登录网页版邮箱 -> 设置 -> 账户 -> POP3/IMAP -> 开启服务 -> 获取授权码
- **Gmail**：开启两步验证 -> 应用专用密码 -> 生成新密码

## 注意事项

1. 请勿将 `config.py` 文件提交到版本控制系统（已被 `.gitignore` 排除）
2. 确保邮箱授权码的安全性，不要泄露给他人
3. 定期更换邮箱授权码以提高安全性
- 示例配置文件 `config_example.py` 仅作参考，请勿在其中存储真实的敏感信息