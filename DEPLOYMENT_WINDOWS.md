# Soft Collar Toolbox 2.0 - Windows 部署指南

## 🪟 Windows 专用快速部署

本指南专为 Windows 用户提供详细的部署说明。

---

## 📋 目录

1. [系统要求](#系统要求)
2. [安装 Docker Desktop](#安装-docker-desktop)
3. [快速部署](#快速部署)
4. [部署脚本说明](#部署脚本说明)
5. [常见问题](#常见问题)
6. [WSL2 vs Hyper-V](#wsl2-vs-hyper-v)

---

## 系统要求

### Windows 版本要求
- **Windows 10** 64位：专业版、企业版或教育版（Build 19041 或更高）
- **Windows 11** 64位：所有版本

### 硬件要求
- **CPU**: 支持虚拟化的 64 位处理器
- **内存**: 最低 4GB，推荐 8GB
- **存储**: 至少 20GB 可用空间

### 启用虚拟化
1. 进入 BIOS/UEFI 设置
2. 启用 Intel VT-x 或 AMD-V
3. 启用 Hyper-V（Windows 功能）

---

## 安装 Docker Desktop

### 步骤 1: 下载 Docker Desktop

访问官网下载：
https://www.docker.com/products/docker-desktop

或使用 winget（Windows 11）：
```powershell
winget install Docker.DockerDesktop
```

### 步骤 2: 安装 Docker Desktop

1. 运行下载的安装程序
2. 选择配置选项：
   - ☑ Enable WSL 2 integration（推荐）
   - ☑ Add shortcut to desktop
3. 等待安装完成
4. 重启计算机

### 步骤 3: 启动 Docker Desktop

1. 从开始菜单启动 Docker Desktop
2. 等待 Docker Engine 启动（系统托盘图标变绿）
3. 打开设置验证配置

### 步骤 4: 验证安装

打开 PowerShell 并运行：
```powershell
docker --version
docker compose version
docker ps
```

---

## 快速部署

### 方式 1: PowerShell 脚本（推荐）

#### 1. 打开 PowerShell

按 `Win + X`，选择"Windows PowerShell (管理员)"

#### 2. 克隆项目

```powershell
cd $HOME\Documents
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
```

#### 3. 启用脚本执行

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. 配置环境变量

```powershell
Copy-Item .env.example .env
notepad .env
```

修改以下配置：
```env
NGINX_PORT=8888
NEXT_PUBLIC_API_URL=http://localhost:8888/api
CORS_ORIGINS=http://localhost:8888
DEBUG=False
```

#### 5. 一键部署

```powershell
.\deploy.ps1 deploy
```

### 方式 2: 批处理脚本（简单）

#### 1. 打开命令提示符

按 `Win + R`，输入 `cmd`，按回车

#### 2. 克隆并进入项目

```cmd
cd %USERPROFILE%\Documents
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
```

#### 3. 配置环境变量

```cmd
copy .env.example .env
notepad .env
```

#### 4. 一键部署

```cmd
deploy.bat deploy
```

### 方式 3: Docker Desktop GUI

#### 1. 准备项目

```powershell
git clone https://github.com/yourusername/ruanlingtools.git
cd ruanlingtools
Copy-Item .env.example .env
```

#### 2. 使用 Docker Desktop

1. 打开 Docker Desktop
2. 点击"Containers"
3. 点击"Create"或从 CLI 导入
4. 选择 docker-compose.yml
5. 点击"Run"

---

## 部署脚本说明

### PowerShell 脚本 (deploy.ps1)

功能最全的部署脚本，支持彩色输出和详细状态。

**基本命令：**
```powershell
.\deploy.ps1 deploy    # 部署应用
.\deploy.ps1 start     # 启动容器
.\deploy.ps1 stop      # 停止容器
.\deploy.ps1 restart   # 重启容器
.\deploy.ps1 status    # 查看状态
.\deploy.ps1 logs      # 查看日志
.\deploy.ps1 health    # 健康检查
```

**查看特定服务日志：**
```powershell
.\deploy.ps1 logs backend
.\deploy.ps1 logs frontend
.\deploy.ps1 logs nginx
```

### 批处理脚本 (deploy.bat)

简化版脚本，兼容性更好。

**基本命令：**
```cmd
deploy.bat deploy      # 部署应用
deploy.bat start       # 启动容器
deploy.bat stop        # 停止容器
deploy.bat status      # 查看状态
deploy.bat logs        # 查看日志
deploy.bat health      # 健康检查
```

### 手动 Docker Compose 命令

如果脚本无法运行，可以直接使用 Docker Compose：

```powershell
# 启动
docker compose up -d

# 停止
docker compose stop

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 重新构建
docker compose build --no-cache
docker compose up -d --force-recreate
```

---

## 常见问题

### 问题 1: Docker Desktop 无法启动

**症状：** Docker Desktop 一直显示"Starting..."

**解决方案：**

1. **重启 Docker Desktop**
   - 右键系统托盘图标 → Quit Docker Desktop
   - 重新启动 Docker Desktop

2. **检查 WSL2**
   ```powershell
   wsl --list --verbose
   wsl --update
   ```

3. **重置 Docker Desktop**
   - 设置 → Troubleshoot → Reset to factory defaults

### 问题 2: 端口被占用

**错误信息：** `Error: bind: address already in use`

**解决方案：**

1. 查找占用端口的进程：
   ```powershell
   netstat -ano | findstr :8888
   ```

2. 终止进程或修改端口：
   ```powershell
   # 修改 .env 文件
   notepad .env
   # 修改 NGINX_PORT=8889
   ```

### 问题 3: PowerShell 脚本无法执行

**错误信息：** `无法加载文件，因为在此系统上禁止运行脚本`

**解决方案：**

```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 或者使用 Bypass 模式运行
PowerShell -ExecutionPolicy Bypass -File .\deploy.ps1 deploy
```

### 问题 4: 访问 localhost 失败

**解决方案：**

1. **检查容器状态**
   ```powershell
   docker compose ps
   ```

2. **检查端口映射**
   ```powershell
   docker ps
   ```

3. **尝试使用 127.0.0.1**
   ```
   http://127.0.0.1:8888
   ```

### 问题 5: 文件权限错误

**症状：** 容器内无法写入文件

**解决方案：**

Windows 上 Docker Desktop 会自动处理文件权限，但如果遇到问题：

1. **检查共享驱动器**
   - Docker Desktop → Settings → Resources → File Sharing
   - 确保项目所在驱动器已共享

2. **使用 WSL2 后端**
   - WSL2 有更好的文件系统性能和权限处理

### 问题 6: 构建速度慢

**解决方案：**

1. **增加 Docker 资源**
   - Docker Desktop → Settings → Resources
   - 增加 CPU 和内存分配

2. **使用 WSL2 后端**
   - WSL2 性能比 Hyper-V 快得多

3. **启用 BuildKit**
   ```powershell
   $env:DOCKER_BUILDKIT=1
   docker compose build
   ```

---

## WSL2 vs Hyper-V

### WSL2（推荐）

**优点：**
- ✅ 更快的文件 I/O 性能
- ✅ 更好的资源管理
- ✅ 启动速度快
- ✅ 与 Linux 工具更好的兼容性

**设置 WSL2：**

1. 启用 WSL2
   ```powershell
   # 以管理员身份运行
   wsl --install
   wsl --set-default-version 2
   ```

2. Docker Desktop 设置
   - Settings → General
   - ☑ Use the WSL 2 based engine

### Hyper-V

**优点：**
- ✅ Windows 10 专业版内置
- ✅ 更好的隔离性

**何时使用：**
- WSL2 不可用时
- 需要更强的隔离性时

---

## 性能优化建议

### 1. 使用 WSL2

WSL2 比 Hyper-V 快 2-3 倍。

### 2. 增加资源分配

Docker Desktop → Settings → Resources:
- **CPU**: 至少 4 核
- **内存**: 至少 4GB
- **磁盘**: 20GB+

### 3. 启用文件共享

Settings → Resources → File Sharing:
- 添加项目所在驱动器

### 4. 关闭不必要的服务

Windows 服务中关闭：
- Windows Search（如果不需要）
- Superfetch/Prefetch

### 5. 使用 SSD

将项目和 Docker 数据存储在 SSD 上。

---

## 防火墙配置

如果需要外部访问：

### Windows Defender 防火墙

1. 控制面板 → 系统和安全 → Windows Defender 防火墙
2. 高级设置 → 入站规则 → 新建规则
3. 端口规则：TCP 8888
4. 允许连接

### PowerShell 快速配置

```powershell
# 以管理员身份运行
New-NetFirewallRule -DisplayName "Toolbox HTTP" -Direction Inbound -LocalPort 8888 -Protocol TCP -Action Allow
```

---

## 卸载和清理

### 完全清理

```powershell
# 停止并删除所有容器
.\deploy.ps1 clean

# 或手动
docker compose down -v --rmi all

# 清理 Docker 系统
docker system prune -a --volumes
```

### 卸载 Docker Desktop

1. 控制面板 → 程序 → 卸载程序
2. 找到 Docker Desktop
3. 右键 → 卸载

---

## 故障诊断工具

### Docker Desktop 诊断

```powershell
# 查看 Docker 信息
docker info
docker version

# 查看系统资源使用
docker stats

# 查看磁盘使用
docker system df
```

### Windows 系统信息

```powershell
# 检查虚拟化
systeminfo | findstr /C:"Virtualization"

# 检查 Hyper-V
Get-WindowsOptionalFeature -FeatureName Microsoft-Hyper-V-All -Online

# 检查 WSL
wsl --status
```

---

## 访问应用

部署成功后：

- **应用主页**: http://localhost:8888
- **API 文档**: http://localhost:8888/docs
- **健康检查**: http://localhost:8888/health

### 从局域网访问

1. 查看本机 IP：
   ```powershell
   ipconfig
   ```

2. 使用 IP 访问：
   ```
   http://192.168.1.xxx:8888
   ```

3. 更新 .env 文件：
   ```env
   NEXT_PUBLIC_API_URL=http://192.168.1.xxx:8888/api
   CORS_ORIGINS=http://192.168.1.xxx:8888
   ```

---

## 技术支持

遇到问题？

1. 查看[常见问题](#常见问题)
2. 检查 Docker Desktop 日志
3. 查看容器日志：`.\deploy.ps1 logs`
4. 提交 Issue 到 GitHub

---

**Windows 部署成功！享受工具箱带来的便利！** 🎉
