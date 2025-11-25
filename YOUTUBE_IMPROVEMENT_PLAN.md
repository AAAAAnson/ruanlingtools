# YouTube功能改进方案

## 📊 现状分析

### 已有功能 ✅
1. **基础KOL搜索** - 支持关键词搜索YouTube频道
2. **多API Key轮换** - 配额用尽自动切换
3. **订阅者过滤** - 可设置最小订阅者数
4. **Engagement计算** - 自动计算视频互动率
5. **跳过Shorts** - 自动过滤60秒以下短视频

### Guide版特性对比

| 功能 | 现有 | Guide版 | 优先级 |
|-----|------|---------|--------|
| **时间范围搜索** | ❌ | ✅ | 🔴 高 |
| **成本估算** | ❌ | ✅ | 🟡 中 |
| **数据库持久化** | ❌ | ✅ | 🔴 高 |
| **历史数据查询** | ❌ | ✅ | 🔴 高 |
| **批量关键词处理** | ❌ | ✅ | 🟢 低 |
| **数据导出(Excel/CSV)** | ❌ | ✅ | 🟡 中 |
| **详细分析报告** | ❌ | ✅ | 🟡 中 |
| **API配额追踪** | ❌ | ✅ | 🟡 中 |
| **断点续传** | ❌ | ✅ | 🟢 低 |
| **进度可视化** | ❌ | ✅ | 🟢 低 |
| **语言检测** | ❌ | ✅ | 🟢 低 |
| **并行分片** | ❌ | ✅ | 🟢 低 |

## 🎯 改进目标

### 阶段一：核心功能增强（P0）

#### 1. 时间范围搜索
**问题：** 当前只能搜索最相关的结果，无法指定时间范围

**解决方案：**
```python
# 后端API增强
class KOLSearchRequest(BaseModel):
    keyword: str
    max_results: int = 50
    min_subscribers: int = 10000
    # 新增字段
    published_after: Optional[str] = None  # ISO 8601 格式: 2023-01-01T00:00:00Z
    published_before: Optional[str] = None
    order_by: str = "relevance"  # relevance, date, viewCount, rating
```

**前端UI变更：**
- 添加日期选择器（开始日期/结束日期）
- 添加快捷选项（最近一年、最近三个月等）
- 添加排序选项下拉菜单

#### 2. 数据库持久化
**问题：** 每次搜索结果不保存，无法查看历史或进行趋势分析

**数据库设计：**
```sql
-- 搜索记录表
CREATE TABLE youtube_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(100) NOT NULL,
    search_params TEXT,  -- JSON格式存储搜索参数
    total_channels INTEGER,
    total_videos INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_created_at (created_at)
);

-- 频道表
CREATE TABLE youtube_channels (
    channel_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200),
    custom_url VARCHAR(100),
    description TEXT,
    country VARCHAR(50),
    subscriber_count INTEGER,
    video_count INTEGER,
    view_count BIGINT,
    thumbnail_url TEXT,
    first_seen_at TIMESTAMP,
    last_updated_at TIMESTAMP,
    INDEX idx_subscriber_count (subscriber_count),
    INDEX idx_country (country)
);

-- 视频表
CREATE TABLE youtube_videos (
    video_id VARCHAR(20) PRIMARY KEY,
    channel_id VARCHAR(50),
    title VARCHAR(200),
    published_at TIMESTAMP,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    engagement_rate DECIMAL(10,4),
    duration_seconds INTEGER,
    thumbnail_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES youtube_channels(channel_id),
    INDEX idx_channel_id (channel_id),
    INDEX idx_published_at (published_at),
    INDEX idx_engagement_rate (engagement_rate)
);

-- 搜索-频道关联表
CREATE TABLE youtube_search_channels (
    search_id INTEGER,
    channel_id VARCHAR(50),
    keyword_videos_count INTEGER,
    keyword_total_views BIGINT,
    keyword_avg_engagement DECIMAL(10,4),
    FOREIGN KEY (search_id) REFERENCES youtube_searches(id),
    FOREIGN KEY (channel_id) REFERENCES youtube_channels(channel_id),
    PRIMARY KEY (search_id, channel_id)
);
```

#### 3. 历史数据查询API
```python
@router.get("/history")
async def get_search_history(
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20
):
    """获取搜索历史记录"""
    pass

@router.get("/history/{search_id}")
async def get_search_detail(search_id: int):
    """获取特定搜索的详细结果"""
    pass

@router.get("/channels/{channel_id}/analytics")
async def get_channel_analytics(channel_id: str):
    """获取频道的历史趋势分析"""
    pass
```

### 阶段二：用户体验优化（P1）

#### 4. 成本估算
```python
@router.post("/estimate-cost")
async def estimate_search_cost(request: KOLSearchRequest):
    """
    估算搜索成本（API配额消耗）

    成本计算：
    - Search API: 100 units per request
    - Videos API: 1 unit per request (batch up to 50 video IDs)
    - Channels API: 1 unit per request (batch up to 50 channel IDs)

    总成本 ≈ 100 (search) + ⌈videos/50⌉ + ⌈channels/50⌉
    """
    return {
        "estimated_cost": calculated_cost,
        "estimated_videos": estimated_videos,
        "estimated_channels": estimated_channels,
        "daily_quota_remaining": 10000 - used_quota
    }
```

#### 5. 数据导出功能
```python
@router.get("/export/{search_id}")
async def export_search_results(
    search_id: int,
    format: str = "excel"  # excel, csv, json
):
    """导出搜索结果到Excel/CSV"""
    # 使用 pandas + openpyxl
    # 包含：频道列表、视频列表、统计摘要
    pass
```

#### 6. 分析报告生成
```python
@router.get("/analytics/keyword/{keyword}")
async def generate_keyword_analytics(keyword: str):
    """
    生成关键词分析报告

    包含：
    - Top频道排名
    - 视频数量趋势
    - 平均Engagement变化
    - 国家分布
    - 发布时间分布
    """
    pass
```

### 阶段三：高级特性（P2）

#### 7. API配额管理
```python
# 新增配额追踪表
CREATE TABLE youtube_api_quota_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_key_index INTEGER,
    operation VARCHAR(50),  # search, videos, channels
    cost INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date DATE,
    INDEX idx_date (date),
    INDEX idx_api_key (api_key_index)
);

@router.get("/api/quota-status")
async def get_quota_status():
    """获取当前API配额使用情况"""
    return {
        "keys": [
            {
                "key_index": 1,
                "used_today": 5000,
                "remaining": 5000,
                "last_reset": "2024-01-01T00:00:00Z"
            }
        ]
    }
```

#### 8. 批量关键词处理
```python
@router.post("/batch-search")
async def batch_kol_search(
    keywords: List[str],
    max_results_per_keyword: int = 50,
    min_subscribers: int = 10000
):
    """批量处理多个关键词"""
    # 后台任务处理
    # 返回任务ID，可查询进度
    pass

@router.get("/batch-search/{task_id}/status")
async def get_batch_search_status(task_id: str):
    """查询批量搜索进度"""
    pass
```

## 🏗️ 技术实现方案

### 数据库迁移工具
```python
# backend/tools/migrate_youtube_schema.py
"""
YouTube数据库结构迁移工具
"""
import sqlite3
from pathlib import Path

def upgrade_schema():
    """升级数据库结构"""
    conn = sqlite3.connect('data/youtube_kol.db')
    cursor = conn.cursor()

    # 执行建表SQL
    # ...

    conn.commit()
    conn.close()
```

### Repository层（数据访问）
```python
# backend/repositories/youtube_repository.py
class YouTubeRepository:
    """YouTube数据访问层"""

    def save_search(self, search_data: dict) -> int:
        """保存搜索记录"""
        pass

    def save_channels(self, channels: List[dict]):
        """批量保存频道数据"""
        pass

    def save_videos(self, videos: List[dict]):
        """批量保存视频数据"""
        pass

    def get_search_history(self, filters: dict) -> List[dict]:
        """获取搜索历史"""
        pass

    def get_channel_analytics(self, channel_id: str) -> dict:
        """获取频道分析数据"""
        pass
```

### 前端UI增强

#### 搜索页面新增功能
```tsx
// frontend/src/app/youtube/page.tsx
interface SearchFilters {
  keyword: string;
  minSubscribers: number;
  maxResults: number;
  // 新增
  publishedAfter?: string;
  publishedBefore?: string;
  orderBy: 'relevance' | 'date' | 'viewCount' | 'rating';
  saveToDatabase: boolean;  // 是否保存到数据库
}
```

#### 新增历史记录页面
```tsx
// frontend/src/app/youtube/history/page.tsx
export default function YouTubeHistoryPage() {
  // 显示搜索历史
  // 支持筛选、排序
  // 可查看详情、导出、删除
}
```

#### 新增分析报告页面
```tsx
// frontend/src/app/youtube/analytics/page.tsx
export default function YouTubeAnalyticsPage() {
  // 显示趋势图表
  // Top频道排行
  // 国家分布饼图
  // 时间分布柱状图
}
```

## 📦 依赖包更新

### Backend
```txt
# requirements.txt 新增
pandas>=2.0.0           # 数据处理
openpyxl>=3.1.0         # Excel导出
xlsxwriter>=3.1.0       # Excel高级格式
alembic>=1.12.0         # 数据库迁移
celery>=5.3.0           # 后台任务（可选）
```

### Frontend
```json
{
  "dependencies": {
    "recharts": "^2.10.0",        // 图表库
    "date-fns": "^3.0.0",          // 日期处理
    "react-datepicker": "^4.25.0", // 日期选择器
    "xlsx": "^0.18.5"              // 前端Excel导出（备用）
  }
}
```

## 🎨 UI/UX设计建议

### 搜索页面布局
```
┌─────────────────────────────────────────┐
│  YouTube KOL Search                      │
├─────────────────────────────────────────┤
│  [ Keyword Input                      ]  │
│  ┌──────────┬──────────┐                │
│  │ Min Subs │ Max Res  │                │
│  └──────────┴──────────┘                │
│  ┌──────────┬──────────┐                │
│  │ From     │ To       │ (Date Pickers) │
│  └──────────┴──────────┘                │
│  [ Order By: ▼ ] [Search] [Estimate]    │
├─────────────────────────────────────────┤
│  Results (XX channels, XX videos)        │
│  [ Export ] [ Save to History ]          │
│  ┌──────────────────────────────────┐   │
│  │ Channel Card with stats...       │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 历史记录页面
```
┌─────────────────────────────────────────┐
│  Search History                          │
├─────────────────────────────────────────┤
│  [ Filter by keyword: _______ ]          │
│  ┌────────────────────────────────────┐ │
│  │ Date  │ Keyword │ Channels │ Action │ │
│  ├────────────────────────────────────┤ │
│  │ 2024  │ AI tech │ 15      │ View   │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🚀 实施计划

### Sprint 1 (Week 1-2): 数据库持久化
- [ ] 设计并创建数据库表结构
- [ ] 实现Repository层
- [ ] 修改service层保存数据
- [ ] 测试数据保存和查询

### Sprint 2 (Week 3-4): 时间范围搜索
- [ ] 后端API支持日期参数
- [ ] 前端添加日期选择器
- [ ] 集成测试
- [ ] 性能优化

### Sprint 3 (Week 5-6): 历史查询和导出
- [ ] 实现历史记录API
- [ ] 实现数据导出功能
- [ ] 前端历史记录页面
- [ ] 导出功能UI

### Sprint 4 (Week 7-8): 分析和报告
- [ ] 实现分析API
- [ ] 前端图表集成
- [ ] 成本估算功能
- [ ] API配额追踪

## 📌 注意事项

1. **向后兼容**: 新API需要兼容现有前端调用
2. **性能考虑**: 大量数据需要分页和索引优化
3. **数据清理**: 定期清理过期数据
4. **错误处理**: 完善API错误处理和重试机制
5. **文档更新**: 同步更新API文档

## 🎯 成功指标

- ✅ 支持任意时间范围搜索
- ✅ 100%搜索记录保存到数据库
- ✅ 历史数据可追溯查询
- ✅ 导出功能正常工作
- ✅ API响应时间 < 2秒（P95）
- ✅ 用户满意度 > 4.5/5

---

**文档版本**: v1.0
**创建日期**: 2024-11-24
**负责人**: Claude AI Assistant
