# SSH 部署命令

## SSH 连接到 NAS
```bash
ssh admin@your-nas-ip
```

## 拉取分支代码
```bash
cd /volume1/docker/ruanlingtools

# 切换并拉取分支
git checkout claude/reddit-keyword-scraper-YNpV0
git pull origin claude/reddit-keyword-scraper-YNpV0
```

## Docker 部署
```bash
# 停止、重新构建、启动
docker-compose down && docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 一键部署（合并命令）
```bash
ssh admin@your-nas-ip "cd /volume1/docker/ruanlingtools && git checkout claude/reddit-keyword-scraper-YNpV0 && git pull origin claude/reddit-keyword-scraper-YNpV0 && docker-compose down && docker-compose up -d --build"
```
