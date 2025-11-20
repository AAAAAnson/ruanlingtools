# YouTube KOL Crawler System - 完整使用指南

## 🎯 系统概述

YouTube KOL Crawler 是一个专业的YouTube数据采集和分析系统，用于：
- 基于关键词批量抓取YouTube视频数据
- 汇总和分析频道（KOL）信息
- 生成详细的数据报告和分析
- 支持多API Key轮换和并行处理

## 📋 功能特性

### 核心功能
- ✅ **全时间窗视频抓取** - 支持任意时间范围的视频采集
- ✅ **智能API管理** - 多Key轮换、配额管理、错误恢复
- ✅ **数据持久化** - SQLite/MySQL数据库存储
- ✅ **进度可视化** - PowerShell ASCII进度条显示
- ✅ **断点续传** - 错误队列管理，支持失败重试

### 增强功能
- ✅ **成本预估** - 采集前预估API消耗
- ✅ **并行分片** - 支持多机并行处理
- ✅ **语言检测** - 自动识别视频语言
- ✅ **国家识别** - 智能推断频道所属国家
- ✅ **数据导出** - Excel/CSV/JSON多格式导出
- ✅ **分析报告** - 自动生成统计分析报告

## 🚀 快速开始

### 1. 系统要求
- Windows 10/11 或 Windows Server
- Python 3.8 或更高版本
- 至少 1GB 可用磁盘空间
- 稳定的网络连接

### 2. 安装步骤

#### 步骤 1: 克隆或下载项目
```powershell
# 进入项目目录
cd D:\yt-kol-crawler\YouTube
```

#### 步骤 2: 安装Python依赖
```powershell
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

#### 步骤 3: 配置API密钥

1. 复制配置模板：
```powershell
copy .env.example .env
```

2. 编辑 `.env` 文件，添加您的YouTube API密钥：
```env
YOUTUBE_API_KEYS=AIzaSyXXXXXXXXXXXXXXXXXX,AIzaSyYYYYYYYYYYYYYYYYYY
```

> ⚠️ **重要**: 您需要先在 [Google Cloud Console](https://console.cloud.google.com/) 创建项目并启用 YouTube Data API v3

### 3. 获取YouTube API密钥

#### 详细步骤：
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3:
   - 导航到 "API和服务" → "库"
   - 搜索 "YouTube Data API v3"
   - 点击启用
4. 创建API密钥:
   - 导航到 "API和服务" → "凭据"
   - 点击 "创建凭据" → "API密钥"
   - 限制密钥（推荐）：
     - API限制：仅限YouTube Data API v3
     - 应用限制：IP地址（添加您的IP）
5. 复制密钥到 `.env` 文件

## 📖 详细使用教程

### 基础用法

#### 1. 爬取单个关键词（使用批处理文件）
```powershell
# 最简单的方式 - 使用批处理文件
.\run_crawler.bat "AI technology"

# 指定起始年份
.\run_crawler.bat "machine learning" --start-year 2023

# 限制结果数量
.\run_crawler.bat "deep learning" --max-results 1000
```

#### 2. 使用PowerShell脚本（高级进度显示）
```powershell
# 单个关键词
.\run_crawler.ps1 -Keywords "AI technology"

# 多个关键词
.\run_crawler.ps1 -Keywords "AI technology","machine learning","deep learning"

# 指定时间范围
.\run_crawler.ps1 -Keywords "ChatGPT" -StartYear 2023 -EndDate "2024-12-31"

# 限制结果数量
.\run_crawler.ps1 -Keywords "GPT-4" -MaxResults 500
```

#### 3. 直接使用Python（最大灵活性）
```powershell
# 基础爬取
python main.py "AI technology"

# 指定完整时间范围
python main.py "machine learning" --start-date "2023-01-01" --end-date "2024-12-31"

# 多个关键词
python main.py "AI" "ML" "DL" --start-year 2023

# 仅估算成本
python main.py "large dataset" --estimate-only
```

### 高级功能

#### 1. API状态管理
```powershell
# 查看API密钥状态
python main.py --status

# 重置每日配额（太平洋时间午夜自动重置）
python main.py --reset-quota

# 处理失败队列
python main.py --process-queue
```

#### 2. 并行处理（多机分片）

在多台机器上并行运行：

**机器1:**
```powershell
.\run_crawler.ps1 -Keywords "AI","ML","DL","NLP" -ShardId 0 -ShardCount 2
```

**机器2:**
```powershell
.\run_crawler.ps1 -Keywords "AI","ML","DL","NLP" -ShardId 1 -ShardCount 2
```

#### 3. 数据分析和报告

```powershell
# 分析特定关键词
python analyzer.py keyword "AI technology"

# 分析特定频道
python analyzer.py channel "UCdKG2JnYDzJO8swEcNomKnw"

# 生成综合报告
python analyzer.py report

# 导出数据到Excel
python analyzer.py export --keyword "AI technology" --format excel

# 导出所有数据
python analyzer.py export --format csv
```

## 📊 数据库结构

系统使用SQLite数据库（默认）或MySQL，包含以下主要表：

### videos 表
- `video_id` - YouTube视频ID
- `keyword` - 搜索关键词
- `title` - 视频标题
- `published_at` - 发布时间
- `channel_id` - 频道ID
- `view_count` - 观看次数
- `like_count` - 点赞数
- `comment_count` - 评论数

### channels 表
- `channel_id` - 频道ID
- `title` - 频道名称
- `custom_url` - 自定义URL
- `country` - 国家/地区
- `subscriber_count` - 订阅者数
- `video_count` - 视频总数
- `view_count` - 总观看次数

## 🔧 配置说明

### 环境变量配置 (.env文件)

```env
# YouTube API配置
YOUTUBE_API_KEYS=key1,key2,key3  # 多个Key用逗号分隔
PER_KEY_BUDGET=9800               # 每个Key的每日配额限制

# 数据库配置
DB_TYPE=sqlite                    # 或 mysql
DB_PATH=./data/youtube_kol.db     # SQLite数据库路径

# MySQL配置（可选）
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=password
# DB_NAME=youtube_kol

# 分片配置
SHARD_ID=0                        # 当前分片ID
SHARD_COUNT=1                     # 总分片数

# 显示配置
KOL_NO_EMOJI=0                    # 1=禁用emoji显示

# 采样配置
SAMPLE_SIZE=100                   # 成本估算采样大小
AUTO_EXPAND_KEYS=0                # 1=自动扩容API Key
```

## 📈 使用场景示例

### 场景1: 研究AI技术趋势
```powershell
# 1. 爬取2023-2024年的AI相关视频
.\run_crawler.ps1 -Keywords "artificial intelligence","AI technology","machine learning" -StartYear 2023

# 2. 分析数据
python analyzer.py keyword "artificial intelligence"

# 3. 导出报告
python analyzer.py export --keyword "artificial intelligence" --format excel
```

### 场景2: 竞品分析
```powershell
# 1. 爬取竞品相关内容
python main.py "competitor product name" --start-year 2024

# 2. 分析top频道
python analyzer.py keyword "competitor product name"

# 3. 导出频道列表
python analyzer.py export --keyword "competitor product name"
```

### 场景3: KOL发现
```powershell
# 1. 爬取行业关键词
.\run_crawler.bat "your industry keyword" --start-year 2023

# 2. 生成报告查看top KOL
python analyzer.py report

# 3. 深入分析特定KOL
python analyzer.py channel "CHANNEL_ID_HERE"
```

## ⚠️ 注意事项

### API配额管理
- 每个Google账号每天有10,000单位的免费配额
- Search操作消耗100单位/次
- Videos和Channels操作消耗1单位/次
- 建议准备3-5个API Key以确保充足配额

### 最佳实践
1. **先估算成本**: 使用 `--estimate-only` 预估API消耗
2. **分批处理**: 对大量关键词分批次处理
3. **定期备份**: 定期备份SQLite数据库文件
4. **监控进度**: 使用PowerShell脚本查看实时进度
5. **错误恢复**: 定期运行 `--process-queue` 处理失败任务

### 常见问题

**Q: API Key配额用完了怎么办？**
A: 系统会自动切换到下一个可用的Key。所有Key都用完后会停止并保存进度，第二天配额重置后可继续。

**Q: 如何提高爬取速度？**
A: 
1. 增加更多API Key
2. 使用多机并行（分片功能）
3. 优化时间窗口大小

**Q: 数据库太大怎么办？**
A: 
1. 定期导出历史数据
2. 使用MySQL替代SQLite
3. 实施数据归档策略

**Q: 爬虫中断了怎么办？**
A: 系统支持断点续传，直接重新运行相同命令即可从中断处继续。

## 🛠️ 故障排除

### 问题1: Python未找到
**解决方案:**
1. 确认Python已安装: `python --version`
2. 添加Python到PATH环境变量
3. 重启PowerShell/命令提示符

### 问题2: API错误 403
**可能原因:**
- API Key无效或被禁用
- 未启用YouTube Data API v3
- IP限制不匹配

**解决方案:**
1. 检查Google Cloud Console中的API状态
2. 重新生成API Key
3. 检查API Key限制设置

### 问题3: 数据库锁定错误
**解决方案:**
1. 确保没有其他进程访问数据库
2. 删除 `.db-journal` 文件（如果存在）
3. 考虑切换到MySQL

## 📞 支持与帮助

如遇到问题，请检查：
1. 日志文件: `./logs/kol_crawler.log`
2. 错误队列: 运行 `python main.py --status` 查看
3. API配额: 在Google Cloud Console查看使用情况

## 📄 许可证

本项目仅供学习和研究使用，请遵守YouTube服务条款和API使用政策。

---

**开发者备注**: 系统已完整实现所有核心和增强功能，可直接投入使用。建议从小规模测试开始，逐步扩大爬取范围。

祝您使用愉快！🚀
