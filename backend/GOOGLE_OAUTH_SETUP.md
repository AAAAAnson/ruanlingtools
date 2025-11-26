# Google OAuth 配置指南

## 问题说明

Google OAuth 不允许使用内网IP地址（如 `192.168.31.199`）作为重定向URI。只接受：
- `localhost` 或 `127.0.0.1`
- 公共域名（如 `.com`, `.org` 等）

## 解决方案

### 方案1：使用 localhost（推荐用于本地开发）

#### 1. 创建 OAuth 凭据

访问 [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

1. 点击 "创建凭据" → "OAuth 2.0 客户端ID"
2. 应用类型：Web应用
3. 名称：YouTube KOL Tools
4. 授权的重定向 URI：
   ```
   http://localhost:6888/api/google-cloud/oauth/callback
   ```
5. 点击"创建"并下载 JSON 文件

#### 2. 配置凭据文件

将下载的 JSON 文件重命名为 `google_oauth_credentials.json` 并放置到 `backend/` 目录下。

文件格式示例：
```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "http://localhost:6888/api/google-cloud/oauth/callback"
    ],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

#### 3. 访问应用

使用 `http://localhost:6888` 访问应用（而不是 `http://192.168.31.199:6888`）

### 方案2：使用 ngrok 隧道（用于远程访问）

如果需要从其他设备访问，可以使用 ngrok：

#### 1. 安装 ngrok

```bash
# 下载并安装 ngrok
# 访问 https://ngrok.com/ 注册并下载
```

#### 2. 启动隧道

```bash
ngrok http 6888
```

会得到一个公共URL，如：`https://xxxx-xx-xxx-xxx-xxx.ngrok.io`

#### 3. 配置 OAuth 重定向

在 Google Cloud Console 中添加重定向 URI：
```
https://xxxx-xx-xxx-xxx-xxx.ngrok.io/api/google-cloud/oauth/callback
```

#### 4. 更新 google_oauth_credentials.json

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "http://localhost:6888/api/google-cloud/oauth/callback",
      "https://xxxx-xx-xxx-xxx-xxx.ngrok.io/api/google-cloud/oauth/callback"
    ],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

### 方案3：配置域名（生产环境）

对于生产环境，建议配置真实域名：

1. 购买域名（如 `yourdomain.com`）
2. 配置 DNS 指向服务器
3. 配置 SSL 证书（推荐使用 Let's Encrypt）
4. 在 Google Cloud Console 中配置重定向 URI：
   ```
   https://yourdomain.com/api/google-cloud/oauth/callback
   ```

## 常见问题

### Q: 为什么不能使用内网IP？
A: Google 的安全策略要求 OAuth 重定向必须使用可验证的域名或 localhost，以防止中间人攻击。

### Q: localhost 和 127.0.0.1 有区别吗？
A: 对于 Google OAuth，建议使用 `localhost`。某些情况下 `127.0.0.1` 可能会有兼容性问题。

### Q: 可以同时配置多个重定向URI吗？
A: 可以。在 `redirect_uris` 数组中可以添加多个URI，方便在不同环境切换。

## 推荐配置（开发环境）

```json
{
  "web": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "http://localhost:6888/api/google-cloud/oauth/callback"
    ],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

访问地址：`http://localhost:6888`

## 注意事项

1. ⚠️ 切勿将 `google_oauth_credentials.json` 提交到 Git
2. ⚠️ 妥善保管 Client Secret
3. ⚠️ 生产环境务必使用 HTTPS
4. ⚠️ 定期轮换凭据以提高安全性
