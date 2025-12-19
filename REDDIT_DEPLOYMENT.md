# Reddit功能部署指南

本指南将帮助你部署Reddit关键词搜索功能到服务器。

## 📋 前置要求

- Git
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选，用于生产部署)

## 🚀 快速部署

### 方式一：拉取分支并合并（推荐）

#### 1. 拉取最新代码

如果你已经在主分支：

```bash
# 进入项目目录
cd /path/to/ruanlingtools

# 拉取最新的远程分支
git fetch origin

# 切换到Reddit功能分支
git checkout claude/reddit-keyword-scraper-YNpV0

# 或者直接拉取并合并到主分支
git checkout main  # 或你的主分支名
git merge claude/reddit-keyword-scraper-YNpV0
```

如果是新克隆项目：

```bash
# 克隆仓库
git clone https://github.com/AAAAAnson/ruanlingtools.git
cd ruanlingtools

# 切换到Reddit功能分支
git checkout claude/reddit-keyword-scraper-YNpV0
```

#### 2. 安装依赖

**后端依赖：**
```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者只安装后端依赖
cd backend
pip install -r requirements.txt
```

**前端依赖：**
```bash
cd frontend
npm install
```

#### 3. 配置环境变量

**后端配置：**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 中配置：
```env
# Reddit API配置
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=linux:ruanlingtools:v1.0 (by /u/your_reddit_username)

# 其他配置...
DEBUG=False
CORS_ORIGINS=http://localhost:8888,http://your-server-ip:8888
```

**前端配置：**
```bash
cd frontend
cp .env.local.example .env.local  # 如果有的话

# 或者直接在.env.local创建
echo "NEXT_PUBLIC_API_URL=http://your-server-ip:8888/api" > .env.local
```

#### 4. 运行项目（开发模式）

**启动后端：**
```bash
cd backend
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**启动前端：**
```bash
cd frontend
npm run dev
```

访问：
- 前端：http://localhost:3000
- 后端API文档：http://localhost:8000/docs

---

### 方式二：使用Docker部署（生产环境推荐）

#### 1. 准备配置

```bash
# 拉取代码（同上）
git clone https://github.com/AAAAAnson/ruanlingtools.git
cd ruanlingtools
git checkout claude/reddit-keyword-scraper-YNpV0

# 配置环境变量
cp .env.example .env
nano .env
```

#### 2. 构建并启动容器

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

#### 3. 访问服务

- 应用：http://your-server-ip:8888
- API文档：http://your-server-ip:8888/docs

#### 4. 常用Docker命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重新构建特定服务
docker-compose up -d --build backend
```

---

## 🔧 Reddit API配置

### 获取Reddit API凭证

1. **访问Reddit Apps页面**
   ```
   https://www.reddit.com/prefs/apps
   ```

2. **创建新应用**
   - 点击 "create app" 或 "create another app"
   - 选择 "script" 类型
   - 填写：
     - Name: ruanlingtools (或任意名称)
     - Description: Reddit keyword search tool
     - Redirect URI: http://localhost:8080

3. **获取凭证**
   - **Client ID**: 在应用名称下方的字符串
   - **Client Secret**: 标记为"secret"的字符串

4. **配置User Agent**
   - 格式：`platform:app_id:version (by /u/your_username)`
   - 例如：`linux:ruanlingtools:v1.0 (by /u/myusername)`

### 两种配置方式

#### 方式A：通过Web界面配置（推荐）

1. 启动应用后，访问设置页面
2. 滚动到 "Reddit API Configuration" 区域
3. 填写三个字段并保存

#### 方式B：通过环境变量配置

在 `.env` 文件中添加：
```env
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_secret
REDDIT_USER_AGENT=linux:ruanlingtools:v1.0 (by /u/yourusername)
```

---

## 📦 更新已部署的项目

### 开发环境更新

```bash
cd /path/to/ruanlingtools

# 拉取最新代码
git fetch origin
git pull origin claude/reddit-keyword-scraper-YNpV0

# 更新后端依赖
pip install -r requirements.txt

# 更新前端依赖
cd frontend
npm install

# 重启服务
# 按Ctrl+C停止当前进程，然后重新启动
```

### Docker环境更新

```bash
cd /path/to/ruanlingtools

# 拉取最新代码
git fetch origin
git pull origin claude/reddit-keyword-scraper-YNpV0

# 重新构建并启动
docker-compose down
docker-compose up -d --build

# 或者只重启特定服务
docker-compose up -d --build backend
```

---

## 🔒 生产环境配置建议

### 1. 安全配置

```env
# .env
DEBUG=False
SECRET_KEY=使用强随机密钥  # 生成：python -c "import secrets; print(secrets.token_hex(32))"

# CORS配置
CORS_ORIGINS=https://yourdomain.com

# API URL
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
```

### 2. Nginx反向代理（可选）

如果使用自己的Nginx：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API文档
    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

### 3. SSL/HTTPS配置

使用Let's Encrypt：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🧪 测试部署

### 1. 测试后端API

```bash
# 健康检查
curl http://localhost:8888/api/health

# 测试Reddit配置状态
curl http://localhost:8888/api/reddit/config

# 测试搜索（需要先配置API）
curl -X POST http://localhost:8888/api/reddit/search \
  -H "Content-Type: application/json" \
  -d '{"keyword":"python","limit":10}'
```

### 2. 测试前端

访问以下页面确认功能：
- http://localhost:8888/ - 主页
- http://localhost:8888/reddit - Reddit搜索页面
- http://localhost:8888/settings - 设置页面

---

## 🐛 故障排查

### 问题1：无法连接到后端

**检查：**
```bash
# 检查后端是否运行
curl http://localhost:8000/api/health

# 检查Docker容器状态
docker-compose ps

# 查看后端日志
docker-compose logs backend
```

**解决：**
- 确认CORS_ORIGINS配置正确
- 确认防火墙允许端口8888/8000
- 检查.env中的配置

### 问题2：Reddit API返回错误

**检查：**
- 确认API凭证正确
- 确认User Agent格式正确
- 查看后端日志：`docker-compose logs backend | grep -i reddit`

**解决：**
- 重新获取Reddit API凭证
- 在Settings页面重新保存配置
- 检查data/settings.json文件内容

### 问题3：前端页面空白

**检查：**
```bash
# 检查前端构建
cd frontend
npm run build

# 查看浏览器控制台错误
```

**解决：**
- 确认NEXT_PUBLIC_API_URL配置正确
- 清除浏览器缓存
- 检查前端日志：`docker-compose logs frontend`

### 问题4：Excel导出失败

**检查：**
- 后端日志中的错误信息
- outputs目录是否有写权限
- openpyxl库是否正确安装

**解决：**
```bash
# 重新安装依赖
pip install openpyxl==3.1.2

# 检查outputs目录权限
ls -la backend/outputs/
chmod 755 backend/outputs/
```

---

## 📊 监控和日志

### Docker环境日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 本地环境日志

- 后端日志：`backend/app.log`
- Nginx日志：`nginx/logs/access.log` 和 `nginx/logs/error.log`

---

## 🔄 版本管理最佳实践

### 开发分支工作流

```bash
# 1. 保持分支最新
git checkout claude/reddit-keyword-scraper-YNpV0
git pull origin claude/reddit-keyword-scraper-YNpV0

# 2. 如果需要合并到主分支
git checkout main
git merge claude/reddit-keyword-scraper-YNpV0

# 3. 解决冲突（如果有）
# 编辑冲突文件后
git add .
git commit -m "Merge Reddit feature"

# 4. 推送到远程
git push origin main
```

### 回滚操作

如果部署出现问题需要回滚：

```bash
# 查看提交历史
git log --oneline

# 回滚到特定提交
git reset --hard <commit-hash>

# 或者只回滚特定文件
git checkout <commit-hash> -- path/to/file
```

---

## 📝 备份建议

### 定期备份

```bash
# 备份数据库/配置文件
tar -czf backup-$(date +%Y%m%d).tar.gz \
  .env \
  data/ \
  backend/app.log

# 备份到远程
scp backup-*.tar.gz user@backup-server:/backups/
```

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

cd /path/to/ruanlingtools
tar -czf "$BACKUP_DIR/ruanlingtools_$DATE.tar.gz" \
  .env data/ backend/app.log

# 删除30天前的备份
find $BACKUP_DIR -name "ruanlingtools_*.tar.gz" -mtime +30 -delete
```

添加到crontab：
```bash
crontab -e
# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

---

## 🎯 性能优化建议

### 1. 数据库优化（如果使用）

```python
# 创建索引
# 在settings.json中定期清理旧数据
```

### 2. 缓存配置

可以添加Redis缓存搜索结果：
```env
REDIS_URL=redis://localhost:6379/0
```

### 3. 前端优化

```bash
# 构建生产版本
cd frontend
npm run build

# 使用PM2管理Node进程
npm install -g pm2
pm2 start npm --name "frontend" -- start
pm2 save
pm2 startup
```

---

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件
2. 检查GitHub Issues
3. 参考项目README.md
4. 查看API文档：http://localhost:8888/docs

---

**部署完成！** 🎉

现在你可以：
1. 访问 http://your-server:8888/settings 配置Reddit API
2. 访问 http://your-server:8888/reddit 开始搜索
3. 享受Reddit关键词搜索功能！
