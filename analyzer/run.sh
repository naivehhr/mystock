#!/bin/bash
# 沪深300 分析脚本 - 手动执行入口

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python 依赖
if ! python3 -c "import akshare" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 执行分析
python3 -u stock_analyzer.py

echo ""
echo "完成! 报告目录: ~/stock-reports/reports/"
