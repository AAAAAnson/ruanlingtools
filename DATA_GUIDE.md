# 📊 数据查看和使用指南

## ✅ 问题已解决

1. **数据位置**: 您的数据存储在 `D:\yt-kol-crawler\YouTube\data\youtube_kol.db`
2. **Excel导出错误**: 已修复
3. **GUI问题**: 已创建修复版 `gui_fixed.py`

## 🔍 查看您的数据

### 方法1: 使用工具批处理（最简单）
```
双击运行 tools.bat
选择选项 1 查看数据摘要
选择选项 2 导出到Excel
```

### 方法2: 直接查看数据摘要
```
.\venv\Scripts\python.exe view_data.py
```

### 方法3: 使用修复后的GUI
```
.\venv\Scripts\python.exe gui_fixed.py
```

### 方法4: 导出数据到Excel
```
# 导出特定关键词数据
.\venv\Scripts\python.exe analyzer.py export --keyword "imyfone" --format excel

# 导出所有数据
.\venv\Scripts\python.exe analyzer.py export --format excel
```

## 📈 数据分析

### 分析特定关键词
```
.\venv\Scripts\python.exe analyzer.py keyword "imyfone"
```

### 生成综合报告
```
.\venv\Scripts\python.exe analyzer.py report
```

## 🗄️ 数据说明

您已经成功爬取了 **699个视频** 和 **389个频道** 的数据！

数据显示 "inserted: 0" 是因为这些数据已经存在于数据库中（避免重复）。

### 数据库内容：
- **videos表**: 包含所有视频的详细信息
  - 标题、描述、观看数、点赞数、评论数等
  - 发布时间、频道信息
  - 检测的语言

- **channels表**: 包含所有频道（KOL）信息
  - 频道名称、自定义URL
  - 订阅者数量、视频总数
  - 国家/地区信息

## 🛠️ 快速操作

### 1. 查看数据摘要
```bash
# 运行这个命令查看您的数据统计
.\venv\Scripts\python.exe view_data.py
```

### 2. 导出到Excel（已修复）
```bash
# 导出imyfone关键词数据到Excel
.\venv\Scripts\python.exe analyzer.py export --keyword "imyfone" --format excel
```

### 3. 使用新的GUI（已修复）
```bash
# 使用修复版GUI
.\venv\Scripts\python.exe gui_fixed.py
```

### 4. 分析数据
```bash
# 分析imyfone关键词
.\venv\Scripts\python.exe analyzer.py keyword "imyfone"
```

## 📁 文件位置

- **数据库**: `data\youtube_kol.db`
- **导出文件**: `data\` 文件夹
- **日志文件**: `logs\kol_crawler.log`

## ⚡ 快速测试

运行以下命令确认一切正常：
```bash
tools.bat
```
然后选择选项 1 查看数据摘要。

## 🎯 下一步建议

1. **导出数据**: 使用 `tools.bat` 选择选项 2 导出到Excel
2. **数据分析**: 在Excel中进行更深入的分析
3. **继续爬取**: 使用其他关键词继续收集数据
4. **KOL筛选**: 根据订阅者数、参与率等指标筛选优质KOL

---

所有问题都已解决！您可以正常使用系统了。🎉
