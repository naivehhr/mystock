# 日志分析 Skill 使用指南

## 📋 简介
这是一个专门用于分析系统日志并生成PDF报告的AI Skill。它可以自动解析日志文件，提取关键信息，并以可视化的方式呈现分析结果。

## 🚀 快速开始

### 1. 基本使用
```bash
# 分析最近7天的日志，生成默认命名的PDF报告
/log-analyze

# 分析最近30天的日志
/log-analyze --days 30

# 指定输出文件名
/log-analyze --output monthly_report.pdf

# 分析特定日志文件
/log-analyze --log-file custom.log --output custom_report.pdf
```

### 2. 命令行参数
```bash
usage: log_skill.py [-h] [--log-file LOG_FILE] [--output OUTPUT] [--days DAYS] [--type {all,error,warning,info}]

日志分析 Skill

optional arguments:
  -h, --help            show this help message and exit
  --log-file LOG_FILE, -f LOG_FILE
                        日志文件路径 (默认: logs/stdout.log)
  --output OUTPUT, -o OUTPUT
                        输出PDF文件路径
  --days DAYS, -d DAYS  分析天数 (默认: 7)
  --type {all,error,warning,info}, -t {all,error,warning,info}
                        分析类型 (默认: all)
```

## 📊 分析内容

### 系统概览
- 总日志数量统计
- 任务执行次数和成功率
- 时间范围分析
- 日志类型分布

### 错误分析
- 错误数量和错误率
- 错误类型分类统计
- 最近错误记录展示
- 错误趋势分析

### 性能指标
- 任务平均执行时间
- 执行时间分布统计
- 最短/最长执行时间
- 性能趋势图表

### 可视化图表
- 日志数量趋势图
- 错误类型分布饼图
- 任务执行时间直方图
- 时间分布热力图

## 📁 输出文件结构

生成的PDF报告包含以下部分：
1. **封面** - 报告标题和生成时间
2. **系统概览** - 核心统计数据表格
3. **日志分布** - 各类型日志占比
4. **错误分析** - 错误详情和分类
5. **性能指标** - 执行效率统计
6. **数据图表** - 可视化分析图表

## ⚙️ 环境要求

### 依赖包
```bash
pip install pandas matplotlib reportlab
```

### 支持的Python版本
- Python 3.7+
- 推荐使用Python 3.9+

### 系统要求
- 支持matplotlib的图形环境
- 足够的磁盘空间存储PDF文件

## 🎯 使用场景

### 1. 系统运维监控
```bash
# 每日系统健康检查
/log-analyze --days 1 --output daily_health_check.pdf
```

### 2. 问题诊断分析
```bash
# 分析错误日志
/log-analyze --type error --days 7 --output error_analysis.pdf
```

### 3. 性能优化评估
```bash
# 月度性能报告
/log-analyze --days 30 --output monthly_performance.pdf
```

### 4. 周期性任务分析
```bash
# 分析定时任务执行情况
/log-analyze --log-file scheduler.log --days 7
```

## 🔧 高级配置

### 自定义日志格式支持
技能支持标准的时间戳格式日志：
```
[2026-02-05 10:00:04.487816] 日志内容...
```

### 扩展分析类型
可以在代码中添加自定义的分析模块：
- 新增日志解析规则
- 扩展统计维度
- 添加特定业务指标

## 📈 输出示例

分析结果摘要示例：
```
📊 分析结果摘要:
   • 总日志数: 277
   • 任务执行: 6 次
   • 成功率: 100.0%
   • 错误数量: 0 个
   • 错误率: 0.00%
   • 平均执行时间: 15.2 秒
```

## 🛠️ 故障排除

### 常见问题

1. **依赖包缺失**
   ```bash
   pip install pandas matplotlib reportlab
   ```

2. **中文字体显示问题**
   确保系统安装了中文字体，或修改代码中的字体设置

3. **内存不足**
   对于超大日志文件，可以减小分析天数或增加系统内存

4. **权限问题**
   确保有读取日志文件和写入输出目录的权限

### 性能优化建议

- 对于大文件分析，建议分批次处理
- 定期清理过期日志文件
- 使用SSD存储提升I/O性能

## 📞 技术支持

如遇到使用问题，请检查：
1. Python环境和依赖包版本
2. 日志文件格式是否正确
3. 磁盘空间是否充足
4. 系统权限设置

## 🔄 更新日志

### v1.0.0 (2026-02-05)
- 初始版本发布
- 基础日志分析功能
- PDF报告生成
- 图表可视化支持