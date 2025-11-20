# YouTube Shorts 检测功能说明

## 功能概述

系统现已支持自动检测和标记YouTube Shorts视频。该功能可以帮助您：
- 识别哪些视频是YouTube Shorts
- 在数据分析中区分Shorts和普通视频
- 导出包含Shorts标识的Excel报表

## Shorts判断标准

系统使用以下标准判断视频是否为YouTube Shorts：

1. **时长标准**：视频时长 ≤ 60秒
2. **标签标准**：视频标题或描述中包含 `#Shorts` 标签（不区分大小写）

满足任一标准即判定为Shorts视频。

## 数据库字段

在 `videos` 表中新增/使用了以下字段：

- `duration_seconds` (INTEGER): 视频时长（秒）
- `is_short` (INTEGER): 是否为Shorts（0=否，1=是）

## 使用方法

### 1. 自动检测（新数据）

当使用爬虫抓取新视频时，系统会自动：
- 解析视频时长
- 检查#Shorts标签
- 设置is_short字段

```bash
# 正常运行爬虫即可
python main.py "关键词"
```

### 2. 更新现有数据

如果您的数据库中已有视频数据，可以运行更新脚本：

```bash
# 更新所有视频的Shorts标识
python update_shorts_field.py
```

### 3. 测试功能

运行测试脚本验证功能是否正常：

```bash
# 测试Shorts检测逻辑
python test_shorts_detection.py
```

### 4. 导出包含Shorts信息的报表

```python
from src.exporter import DataExporter

exporter = DataExporter()

# 导出某个关键词的视频（包含Shorts标识）
exporter.export_videos_report(
    keyword="AI technology",
    output_format="excel"
)
```

导出的Excel文件将包含以下Shorts相关列：
- **Duration (seconds)**: 视频时长（秒）
- **Is Short**: 是否为Shorts（Yes/No）

### 5. 使用批处理工具

运行 `shorts_tools.bat` 可以快速访问所有Shorts相关功能：

```bash
shorts_tools.bat
```

## API使用示例

### 查询所有Shorts视频

```python
from src.database import get_db, Video

db = get_db()
session = db.get_session()

# 查询所有Shorts
shorts = session.query(Video).filter(Video.is_short == 1).all()

# 查询特定关键词的Shorts
keyword_shorts = session.query(Video).filter(
    Video.keyword == "AI",
    Video.is_short == 1
).all()

session.close()
```

### 统计Shorts占比

```python
from sqlalchemy import func

# 统计总体Shorts占比
total_videos = session.query(func.count(Video.video_id)).scalar()
total_shorts = session.query(func.count(Video.video_id)).filter(Video.is_short == 1).scalar()
shorts_percentage = (total_shorts / total_videos * 100) if total_videos > 0 else 0

print(f"Shorts占比: {shorts_percentage:.2f}%")

# 按关键词统计
stats = session.query(
    Video.keyword,
    func.count(Video.video_id).label('total'),
    func.sum(Video.is_short).label('shorts_count')
).group_by(Video.keyword).all()

for keyword, total, shorts_count in stats:
    percentage = (shorts_count / total * 100) if total > 0 else 0
    print(f"{keyword}: {shorts_count}/{total} ({percentage:.1f}%)")
```

## 注意事项

1. **时长解析**：系统使用ISO 8601格式解析YouTube视频时长（如 `PT1M30S` = 1分30秒）

2. **标签检测**：系统检测 `#shorts` 标签时不区分大小写，支持以下格式：
   - `#Shorts`
   - `#shorts`
   - `#SHORTS`

3. **性能影响**：Shorts检测在数据获取时进行，不会显著影响爬虫性能

4. **数据更新**：如果YouTube改变了Shorts的定义或标准，可能需要更新检测逻辑

## 常见问题

**Q: 为什么有些明显是Shorts的视频没有被标记？**
A: 可能原因：
- 视频时长刚好超过60秒（如61秒）
- 视频没有使用#Shorts标签
- 数据抓取时视频信息不完整

**Q: 如何处理时长刚好60秒的视频？**
A: 系统将时长≤60秒的视频都标记为Shorts，包括刚好60秒的视频。

**Q: 能否自定义Shorts的判断标准？**
A: 可以修改 `src/crawler.py` 中的 `_extract_video_data` 方法来自定义判断逻辑。

## 更新日志

- **2024-12-19**: 添加YouTube Shorts自动检测功能
  - 支持基于时长的检测
  - 支持基于#Shorts标签的检测
  - 添加批量更新工具
  - Excel导出包含Shorts标识
