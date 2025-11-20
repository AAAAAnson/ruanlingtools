# 🚀 YouTube Shorts 功能 - 快速开始指南

## 当前状态
✅ 依赖已安装
❌ 数据库缺少Shorts字段

## 立即解决方案

### 在PowerShell中运行以下命令：

```powershell
# 1. 进入项目目录
cd D:\yt-kol-crawler\YouTube

# 2. 运行数据库迁移（添加Shorts字段）
python migrate_database.py

# 3. 测试功能（不需要数据库）
python test_shorts_simple.py

# 4. 如果有现有数据，更新Shorts标识
python update_shorts_field.py
```

### 或者使用批处理文件（更简单）：

```powershell
# 运行设置向导
.\shorts_setup.bat

# 选择选项 1（首次设置）
```

## 🔧 手动修复步骤

如果自动迁移失败，可以手动添加字段：

### 方法1: 使用SQLite工具
```sql
-- 打开SQLite数据库
sqlite3 data/youtube_kol.db

-- 添加字段
ALTER TABLE videos ADD COLUMN duration_seconds INTEGER DEFAULT 0;
ALTER TABLE videos ADD COLUMN is_short INTEGER DEFAULT 0;

-- 退出
.quit
```

### 方法2: 创建新数据库
```powershell
# 删除旧数据库（如果没有重要数据）
Remove-Item data/youtube_kol.db

# 运行爬虫创建新数据库
python main.py "test keyword"
```

## 📋 功能验证

### 1. 简单测试（不需要数据库）
```powershell
python test_shorts_simple.py
```

### 2. 完整测试（需要数据库）
```powershell
# 先运行数据库迁移
python migrate_database.py

# 然后运行测试
python test_shorts_detection.py
```

### 3. 检查数据库字段
```powershell
# 使用Python检查
python -c "
import sqlite3
conn = sqlite3.connect('data/youtube_kol.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(videos)')
columns = cursor.fetchall()
print('Videos表字段:')
for col in columns:
    print(f'  - {col[1]}')
conn.close()
"
```

## ✅ 预期结果

成功后，videos表应该包含以下Shorts相关字段：
- `duration` - 原始时长格式（如PT1M30S）
- `duration_seconds` - 时长（秒）
- `is_short` - 是否为Shorts（0/1）

## 📊 使用Shorts功能

### 1. 新数据自动检测
```powershell
# 运行爬虫时会自动检测Shorts
python main.py "YouTube Shorts"
```

### 2. 更新现有数据
```powershell
# 为已有视频添加Shorts标识
python update_shorts_field.py
```

### 3. 分析Shorts数据
```powershell
# 运行Shorts分析
python shorts_analyzer.py
```

### 4. 导出报告
```powershell
# 导出包含Shorts标识的Excel
python -c "from src.exporter import DataExporter; e=DataExporter(); e.export_videos_report('关键词', output_format='excel')"
```

## ❓ 常见问题

### Q: 提示"no such column: videos.is_short"
A: 运行 `python migrate_database.py` 添加字段

### Q: 提示"No module named 'xxx'"
A: 运行 `pip install xxx` 安装缺失的包

### Q: 数据库文件不存在
A: 运行 `python main.py "test"` 创建数据库

### Q: 想要重新开始
A: 删除 `data` 文件夹，重新运行设置

## 📞 需要帮助？

如果问题仍未解决，请提供以下信息：
1. 错误信息的完整截图
2. Python版本：`python --version`
3. 已安装的包：`pip list`
4. 数据库状态：是否存在 `data/youtube_kol.db`

---
更新时间：2024-12-19
