#!/bin/bash
# Reddit功能快速部署脚本

set -e  # 遇到错误立即退出

echo "🚀 开始部署Reddit搜索功能..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误：请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 1. 检查Git分支
echo -e "${YELLOW}📋 检查当前分支...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "claude/reddit-keyword-scraper-YNpV0" ]; then
    echo -e "${YELLOW}🔄 切换到Reddit功能分支...${NC}"
    git fetch origin
    git checkout claude/reddit-keyword-scraper-YNpV0
    echo -e "${GREEN}✅ 已切换到 claude/reddit-keyword-scraper-YNpV0${NC}"
fi

# 2. 拉取最新代码
echo ""
echo -e "${YELLOW}⬇️  拉取最新代码...${NC}"
git pull origin claude/reddit-keyword-scraper-YNpV0
echo -e "${GREEN}✅ 代码已更新${NC}"

# 3. 检查并配置环境变量
echo ""
echo -e "${YELLOW}⚙️  检查环境配置...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 .env文件不存在，创建中...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env文件已创建${NC}"
    echo -e "${RED}⚠️  请编辑 .env 文件配置Reddit API凭证${NC}"
    echo ""
    read -p "是否现在编辑.env文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo -e "${GREEN}✅ .env文件已存在${NC}"
fi

# 4. 选择部署方式
echo ""
echo -e "${YELLOW}📦 选择部署方式：${NC}"
echo "1) Docker部署（推荐，适合生产环境）"
echo "2) 本地开发模式"
echo "3) 仅安装依赖"
echo ""
read -p "请选择 (1-3): " -n 1 -r
echo

case $REPLY in
    1)
        echo ""
        echo -e "${YELLOW}🐳 使用Docker部署...${NC}"

        # 检查Docker
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
            exit 1
        fi

        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}❌ Docker Compose未安装，请先安装Docker Compose${NC}"
            exit 1
        fi

        # 停止现有容器
        echo "停止现有容器..."
        docker-compose down

        # 构建并启动
        echo "构建并启动容器..."
        docker-compose up -d --build

        # 等待服务启动
        echo "等待服务启动..."
        sleep 10

        # 检查服务状态
        echo ""
        echo -e "${YELLOW}📊 检查服务状态...${NC}"
        docker-compose ps

        echo ""
        echo -e "${GREEN}✅ Docker部署完成！${NC}"
        echo ""
        echo "访问地址："
        echo "  - 应用: http://localhost:8888"
        echo "  - API文档: http://localhost:8888/docs"
        echo "  - Reddit搜索: http://localhost:8888/reddit"
        echo ""
        echo "查看日志："
        echo "  docker-compose logs -f"
        ;;

    2)
        echo ""
        echo -e "${YELLOW}💻 本地开发模式部署...${NC}"

        # 检查Python
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}❌ Python 3未安装${NC}"
            exit 1
        fi

        # 检查Node.js
        if ! command -v node &> /dev/null; then
            echo -e "${RED}❌ Node.js未安装${NC}"
            exit 1
        fi

        # 安装后端依赖
        echo ""
        echo -e "${YELLOW}📦 安装Python依赖...${NC}"
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Python依赖安装完成${NC}"

        # 安装前端依赖
        echo ""
        echo -e "${YELLOW}📦 安装Node.js依赖...${NC}"
        cd frontend
        npm install
        cd ..
        echo -e "${GREEN}✅ Node.js依赖安装完成${NC}"

        echo ""
        echo -e "${GREEN}✅ 本地开发环境配置完成！${NC}"
        echo ""
        echo "启动服务："
        echo ""
        echo "  终端1 - 启动后端："
        echo "    cd backend"
        echo "    python main.py"
        echo ""
        echo "  终端2 - 启动前端："
        echo "    cd frontend"
        echo "    npm run dev"
        echo ""
        echo "访问地址："
        echo "  - 前端: http://localhost:3000"
        echo "  - 后端API: http://localhost:8000/docs"
        ;;

    3)
        echo ""
        echo -e "${YELLOW}📦 安装依赖...${NC}"

        # 安装后端依赖
        echo "安装Python依赖..."
        pip install -r requirements.txt

        # 安装前端依赖
        echo "安装Node.js依赖..."
        cd frontend
        npm install
        cd ..

        echo -e "${GREEN}✅ 依赖安装完成${NC}"
        ;;

    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo -e "${YELLOW}📝 下一步操作：${NC}"
echo "1. 访问设置页面配置Reddit API凭证"
echo "2. 参考 REDDIT_DEPLOYMENT.md 获取详细配置说明"
echo "3. 开始使用Reddit搜索功能"
echo ""
echo -e "${YELLOW}📚 获取Reddit API凭证：${NC}"
echo "  https://www.reddit.com/prefs/apps"
echo ""
