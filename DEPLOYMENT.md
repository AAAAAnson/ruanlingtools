# Soft Collar Toolbox 2.0 - 部署文档

## 📋 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)  
3. [详细部署步骤](#详细部署步骤)
4. [Synology NAS 部署](#synology-nas-部署)
5. [环境变量配置](#环境变量配置)
6. [常用管理命令](#常用管理命令)
7. [故障排除](#故障排除)

---

## 系统要求

### 最低要求
- **CPU**: 2 核心
- **内存**: 2GB RAM
- **存储**: 10GB 可用空间
- **Docker**: 20.10.0+
- **Docker Compose**: 2.0.0+

### 推荐配置
- **CPU**: 4 核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间

---

## 快速开始

### 1. 克隆项目

\`\`\`bash
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
\`\`\`

### 2. 配置环境变量

\`\`\`bash
cp .env.example .env
nano .env
\`\`\`

### 3. 一键部署

\`\`\`bash
chmod +x deploy.sh
./deploy.sh deploy
\`\`\`

### 4. 访问应用

- **应用主页**: http://your-server-ip:8888
- **API 文档**: http://your-server-ip:8888/docs

---

## 详细部署步骤

### 步骤 1: 安装 Docker

**Ubuntu/Debian:**
\`\`\`bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker \$USER
\`\`\`

### 步骤 2: 安装 Docker Compose

\`\`\`bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
\`\`\`

### 步骤 3: 配置环境

\`\`\`bash
cp .env.example .env
# 编辑 .env 文件，修改以下关键配置：
# - NGINX_PORT (默认 8888)
# - NEXT_PUBLIC_API_URL
# - CORS_ORIGINS
\`\`\`

### 步骤 4: 部署

\`\`\`bash
./deploy.sh deploy
\`\`\`

---

## Synology NAS 部署

### SSH 部署

1. 启用 SSH (DSM > 控制面板 > 终端机和 SNMP)
2. SSH 连接到 NAS
3. 执行部署命令：

\`\`\`bash
cd /volume1/docker
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
cp .env.example .env
vi .env
./deploy.sh deploy
\`\`\`

### 配置反向代理

DSM > 控制面板 > 登录门户 > 高级 > 反向代理服务器

- 来源: your-domain.synology.me/toolbox
- 目标: localhost:8888

---

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| NGINX_PORT | Nginx 端口 | 8888 |
| NEXT_PUBLIC_API_URL | API 地址 | http://localhost:8888/api |
| CORS_ORIGINS | CORS 源 | http://localhost:8888 |
| DEBUG | 调试模式 | False |

---

## 常用管理命令

\`\`\`bash
./deploy.sh start      # 启动服务
./deploy.sh stop       # 停止服务
./deploy.sh restart    # 重启服务
./deploy.sh status     # 查看状态
./deploy.sh logs       # 查看日志
./deploy.sh health     # 健康检查
./deploy.sh update     # 更新应用
./deploy.sh clean      # 清理容器
\`\`\`

---

## 故障排除

### 端口被占用

\`\`\`bash
sudo lsof -i :8888
# 修改 .env 中的 NGINX_PORT
\`\`\`

### 查看日志

\`\`\`bash
docker-compose logs -f backend
docker-compose logs -f frontend
\`\`\`

### 重新构建

\`\`\`bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
\`\`\`

---

## 备份数据

\`\`\`bash
# 备份上传文件
docker run --rm -v ruanlingtools_backend-uploads:/data -v \$(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .

# 备份配置
tar czf config-backup.tar.gz .env docker-compose.yml nginx/
\`\`\`

---

**部署成功后，请享受工具箱带来的便利！** 🎉
