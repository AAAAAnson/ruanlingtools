#!/bin/bash
# Reddit功能更新脚本

set -e

echo "🔄 更新Reddit搜索功能..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 拉取最新代码
echo -e "${YELLOW}⬇️  拉取最新代码...${NC}"
git fetch origin
git pull origin claude/reddit-keyword-scraper-YNpV0
echo -e "${GREEN}✅ 代码已更新${NC}"

# 2. 更新依赖
echo ""
echo -e "${YELLOW}📦 更新依赖...${NC}"

# 检查是否使用Docker
if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q "Up"; then
    echo "检测到Docker环境，重新构建容器..."
    docker-compose down
    docker-compose up -d --build
    echo -e "${GREEN}✅ Docker容器已更新${NC}"
else
    echo "更新Python依赖..."
    pip install -r requirements.txt

    echo "更新Node.js依赖..."
    cd frontend
    npm install
    cd ..

    echo -e "${GREEN}✅ 依赖已更新${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  请手动重启服务${NC}"
fi

echo ""
echo -e "${GREEN}🎉 更新完成！${NC}"
