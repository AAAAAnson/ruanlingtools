# NAS 部署配置说明

## 配置步骤

### 1. 获取 NAS 的 IP 地址
在 NAS 上运行：
```bash
hostname -I | cut -d' ' -f1
```

### 2. 配置前端环境变量
在 NAS 上复制示例文件并配置：
```bash
cd /volume2/web/ruanlingtools/frontend
cp .env.local.example .env.local
# 编辑文件，将 YOUR_NAS_IP 替换为实际的 NAS IP 地址
nano .env.local
```

或者直接创建：
```bash
cd /volume2/web/ruanlingtools/frontend
echo "NEXT_PUBLIC_API_URL=http://你的NAS_IP:8000" > .env.local
```

替换 `你的NAS_IP` 为第一步获取的实际 IP 地址。

### 3. 重启前端服务
```bash
# 找到并停止当前的前端进程
ps aux | grep "next"
kill -9 <进程ID>

# 重新启动前端
cd /volume2/web/ruanlingtools/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
```

### 4. 访问应用
在浏览器中访问：`http://你的NAS_IP:3000`

## 自动启动配置（Synology 任务计划）

创建两个任务：

**后端任务：**
- 触发条件：开机
- 用户：你的用户名
- 命令：
```bash
cd /volume2/web/ruanlingtools/backend && nohup python3 main.py > /tmp/backend.log 2>&1 &
```

**前端任务：**
- 触发条件：开机
- 用户：你的用户名
- 命令：
```bash
cd /volume2/web/ruanlingtools/frontend && nohup npm run dev > /tmp/frontend.log 2>&1 &
```

## 检查服务状态

```bash
# 检查后端
curl http://localhost:8000/api/health

# 检查前端
curl http://localhost:3000

# 查看进程
ps aux | grep -E "python3 main.py|next"
```
