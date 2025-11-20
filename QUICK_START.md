# 🚀 YouTube KOL Crawler - 快速启动指南

## 一键安装和使用（最简单）

### 第1步：安装
双击运行 `setup.bat`，它会自动：
- ✅ 检查Python环境
- ✅ 安装所有依赖
- ✅ 创建必要目录
- ✅ 生成配置文件

### 第2步：配置API密钥
1. 打开生成的 `.env` 文件（记事本会自动打开）
2. 将这一行：
   ```
   YOUTUBE_API_KEYS=YOUR_KEY1,YOUR_KEY2,YOUR_KEY3
   ```
   替换为您的实际API密钥：
   ```
   YOUTUBE_API_KEYS=AIzaSyAbcd1234567890,AIzaSyBxyz9876543210
   ```
3. 保存并关闭文件

### 第3步：开始使用

#### 方式A：使用图形界面（最简单）
```
双击 gui.py 或运行：python gui.py
```

#### 方式B：使用命令行
```
run_crawler.bat "您的关键词"
```

---

## 📝 获取YouTube API密钥（必需）

### 快速步骤：
1. **访问** https://console.cloud.google.com/
2. **创建项目**：点击"创建项目"，输入项目名称
3. **启用API**：
   - 点击"启用API和服务"
   - 搜索"YouTube Data API v3"
   - 点击"启用"
4. **创建密钥**：
   - 点击"创建凭据" → "API密钥"
   - 复制生成的密钥
5. **设置限制**（推荐）：
   - 点击密钥名称
   - 在"API限制"中选择"限制密钥"
   - 勾选"YouTube Data API v3"
   - 保存

---

## 💡 常用命令示例

### 基础爬取
```bash
# 爬取单个关键词
run_crawler.bat "AI technology"

# 爬取多个关键词
run_crawler.bat "AI" "machine learning" "deep learning"

# 指定起始年份
run_crawler.bat "ChatGPT" --start-year 2023

# 限制结果数量
run_crawler.bat "GPT-4" --max-results 500
```

### 数据分析
```bash
# 分析关键词数据
python analyzer.py keyword "AI technology"

# 导出Excel报表
python analyzer.py export --keyword "AI technology" --format excel

# 生成总体报告
python analyzer.py report
```

### 系统管理
```bash
# 查看API状态
python main.py --status

# 处理失败任务
python main.py --process-queue

# 仅估算成本
python main.py "big data" --estimate-only
```

---

## ❓ 常见问题快速解决

### 问题：提示"Python未找到"
**解决**：
1. 下载Python：https://www.python.org/downloads/
2. 安装时勾选"Add Python to PATH"
3. 重启电脑

### 问题：API配额用完
**解决**：
1. 等待第二天自动重置（太平洋时间午夜）
2. 或添加更多API密钥到.env文件

### 问题：爬取速度慢
**解决**：
1. 添加更多API密钥（用逗号分隔）
2. 使用多个关键词并行爬取

### 问题：数据在哪里？
**位置**：
- 数据库：`./data/youtube_kol.db`
- 导出文件：`./data/`目录
- 日志：`./logs/`目录

---

## 📊 查看结果

### 方式1：使用分析工具
```bash
python analyzer.py keyword "您的关键词"
```

### 方式2：导出到Excel
```bash
python analyzer.py export --format excel
```
然后打开 `./data/` 目录中的Excel文件

### 方式3：使用数据库工具
使用任何SQLite查看工具打开 `./data/youtube_kol.db`

---

## 🎯 三步快速测试

1. **安装**：双击 `setup.bat`
2. **配置**：编辑 `.env` 添加API密钥
3. **测试**：运行 `run_crawler.bat "test" --max-results 10`

如果能看到进度条和数据，说明系统正常工作！

---

## 📧 需要帮助？

1. 查看详细文档：`README.md`
2. 查看日志文件：`./logs/kol_crawler.log`
3. 运行状态检查：`python main.py --status`

祝您使用愉快！🎉
