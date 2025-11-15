# Soft Collar Toolbox 2.0 🎨

像素风格的多功能工具平台 - 隐私优先、简单高效

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Docker](https://img.shields.io/badge/docker-required-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ 功能特性

### 📸 图片处理工具
- **格式转换**: JPG ↔ PNG ↔ WebP
- 批量处理、实时预览

### 📝 文本处理工具（5个）
- **大小写转换器**: 11种转换类型
- **文本格式化器**: 去重、排序、添加行号
- **编码器/解码器**: Base64、URL、HTML、Hex、Binary
- **文本排序器**: 4种排序方式
- **文本统计**: 8项指标实时统计

### 📄 PDF 处理工具（4个）
- **PDF 合并**: 多文件合并，可调整顺序
- **PDF 拆分**: 灵活的页码范围语法
- **文本提取**: 提取所有页面文本
- **PDF 信息**: 查看元数据和属性

### 🎯 设计特色
- 🎮 **8-bit 像素艺术风格** - 复古游戏美学
- 🔒 **隐私优先** - 文本工具全部浏览器端处理
- 🚀 **快速响应** - 优化的性能和用户体验
- 📱 **响应式设计** - 支持各种屏幕尺寸

---

## 🚀 快速开始

### Windows 用户

**方式 1: PowerShell（推荐）**
```powershell
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
Copy-Item .env.example .env
.\deploy.ps1 deploy
```

**方式 2: 批处理**
```cmd
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
copy .env.example .env
deploy.bat deploy
```

📖 **详细指南**: [DEPLOYMENT_WINDOWS.md](DEPLOYMENT_WINDOWS.md)

### Linux / macOS 用户

```bash
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
cp .env.example .env
chmod +x deploy.sh
./deploy.sh deploy
```

📖 **详细指南**: [DEPLOYMENT.md](DEPLOYMENT.md)

### 访问应用

部署成功后，访问：
- 🌐 **应用主页**: http://localhost:8888
- 📚 **API 文档**: http://localhost:8888/docs

---

## 📋 系统要求

| 组件 | 要求 |
|------|------|
| **Docker** | 20.10.0+ |
| **Docker Compose** | 2.0.0+ |
| **CPU** | 2核心（推荐4核心） |
| **内存** | 2GB（推荐4GB） |
| **存储** | 10GB 可用空间 |

### Windows 特殊要求
- Windows 10/11 64位
- 启用虚拟化（VT-x/AMD-V）
- Docker Desktop for Windows

---

## 🛠️ 技术栈

### 前端
- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript (严格模式)
- **样式**: Tailwind CSS
- **动画**: Framer Motion
- **图标**: Lucide React

### 后端
- **框架**: FastAPI
- **语言**: Python 3.11+
- **图片处理**: Pillow
- **PDF处理**: PyPDF2
- **验证**: Pydantic

### 基础设施
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **编码标准**: UTF-8 强制规范

---

## 📂 项目结构

```
ruanlingtools/
├── frontend/               # Next.js 前端应用
│   ├── src/
│   │   ├── app/           # 页面路由
│   │   │   ├── image/     # 图片工具
│   │   │   ├── text/      # 文本工具
│   │   │   └── pdf/       # PDF工具
│   │   └── components/    # 像素风格组件
│   └── Dockerfile         # 前端镜像（多阶段构建）
│
├── backend/               # FastAPI 后端应用
│   ├── routers/          # API 路由
│   ├── services/         # 业务逻辑
│   ├── models/           # 数据模型
│   └── Dockerfile        # 后端镜像（多阶段构建）
│
├── nginx/                # Nginx 配置
│   ├── nginx.conf       # 主配置
│   └── conf.d/          # 站点配置
│
├── docker-compose.yml   # 容器编排
├── .env.example         # 环境变量模板
│
├── deploy.sh            # Linux/macOS 部署脚本
├── deploy.ps1           # Windows PowerShell 脚本
├── deploy.bat           # Windows 批处理脚本
│
├── DEPLOYMENT.md        # Linux/macOS 部署文档
└── DEPLOYMENT_WINDOWS.md # Windows 部署文档
```

---

## 🎮 管理命令

### Linux / macOS

```bash
./deploy.sh deploy    # 部署应用
./deploy.sh start     # 启动服务
./deploy.sh stop      # 停止服务
./deploy.sh restart   # 重启服务
./deploy.sh status    # 查看状态
./deploy.sh logs      # 查看日志
./deploy.sh health    # 健康检查
./deploy.sh update    # 更新应用
./deploy.sh clean     # 清理容器
```

### Windows PowerShell

```powershell
.\deploy.ps1 deploy   # 部署应用
.\deploy.ps1 start    # 启动服务
.\deploy.ps1 stop     # 停止服务
.\deploy.ps1 status   # 查看状态
.\deploy.ps1 logs     # 查看日志
.\deploy.ps1 health   # 健康检查
```

### Windows 批处理

```cmd
deploy.bat deploy     # 部署应用
deploy.bat start      # 启动服务
deploy.bat stop       # 停止服务
deploy.bat status     # 查看状态
deploy.bat logs       # 查看日志
```

---

## 🔧 配置说明

### 环境变量 (.env)

```env
# 端口配置
NGINX_PORT=8888

# API 地址（前端调用后端）
NEXT_PUBLIC_API_URL=http://localhost:8888/api

# CORS 配置
CORS_ORIGINS=http://localhost:8888

# 调试模式（生产环境设为 False）
DEBUG=False
```

### 不同场景配置

**本地开发：**
```env
NGINX_PORT=8888
NEXT_PUBLIC_API_URL=http://localhost:8888/api
DEBUG=True
```

**内网部署：**
```env
NGINX_PORT=8888
NEXT_PUBLIC_API_URL=http://192.168.1.100:8888/api
CORS_ORIGINS=http://192.168.1.100:8888
```

**Synology NAS：**
```env
NGINX_PORT=8888
NEXT_PUBLIC_API_URL=https://yourdomain.synology.me/toolbox/api
CORS_ORIGINS=https://yourdomain.synology.me
```

---

## 🏗️ 开发路线图

- [x] **P0**: 框架搭建和基础组件
- [x] **P1**: 图片格式转换工具
- [x] **P2**: 文本处理工具套件（5个工具）
- [x] **P3**: PDF 处理工具套件（4个工具）
- [x] **P4**: 部署优化和文档完善
- [ ] **P5**: 更多工具和功能扩展

---

## 📖 文档

- [Linux/macOS 部署指南](DEPLOYMENT.md) - 详细的 Linux 和 macOS 部署文档
- [Windows 部署指南](DEPLOYMENT_WINDOWS.md) - Windows 专用部署说明
- [API 文档](http://localhost:8888/docs) - 部署后可访问的交互式 API 文档

---

## 🐛 故障排除

### 常见问题

**1. 端口被占用**
```bash
# Linux/macOS
sudo lsof -i :8888

# Windows
netstat -ano | findstr :8888
```
解决：修改 `.env` 中的 `NGINX_PORT`

**2. Docker 未启动**
- Linux: `sudo systemctl start docker`
- Windows: 启动 Docker Desktop

**3. 权限错误**
- Linux: `sudo usermod -aG docker $USER`
- Windows: 以管理员身份运行

更多问题请查看详细部署文档。

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🌟 特别感谢

- [Next.js](https://nextjs.org/) - React 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [Docker](https://www.docker.com/) - 容器化平台
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- 所有开源贡献者

---

## 📞 联系方式

- GitHub Issues: [提交问题](https://github.com/yourusername/ruanlingtools/issues)
- Email: your.email@example.com

---

<div align="center">

**用像素艺术打造的现代工具箱** 🎨

Made with ❤️ and pixels

</div>
