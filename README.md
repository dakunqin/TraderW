# TraderW

TraderW 是一个面向 MT4/MT5 的轻量 “终端同步 + Web 控制台” 项目：
- EA（MT4/MT5）定时把账号、挂单、持仓同步到后端
- Web 页面展示账户/订单/持仓，并通过 actions 下发平仓指令给 EA 执行
- 支持 MT4/MT5 账号区分展示（platform 字段）

项目目录结构（核心）
- `ea/`：EA 源码（`TraderW_Relay_MT4.mq4`、`TraderW_Relay_MT5.mq5`）
- `api/`：FastAPI 后端（鉴权、存储、actions、找回密码）
- `src/`：React 前端

## 端口与访问方式

常用端口约定
- 后端 API：`8800`（开发/部署都建议统一）
- 前端开发服务器：`5173`（Vite，带热更新）

同端口模式（推荐用于部署 / 本机无热更新预览）
- 只启动后端一个服务：`http://127.0.0.1:8800/` 同时提供页面与 `/api/...`

## 本机开发启动（Windows）

### 1) 启动后端

```powershell
cd E:\EAs\TraderW\api
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8800
```

健康检查：打开 `http://127.0.0.1:8800/health`

数据库文件（本机直跑默认）：`api/app.db`

### 2) 启动前端（热更新）

```powershell
cd E:\EAs\TraderW
npm ci
npm run dev -- --host 0.0.0.0 --port 5173
```

推荐配置前端指向后端（可选）
- 复制 `.env.example` 为 `.env`
- 设置 `VITE_API_BASE=http://127.0.0.1:8800`

### 3) 本机同端口启动（无热更新，接近部署形态）

```powershell
cd E:\EAs\TraderW
npm ci
npm run build

cd E:\EAs\TraderW\api
.\.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8800
```

访问 `http://127.0.0.1:8800/`

## Docker 部署（单容器，推荐）

项目根目录已提供单容器构建方式：构建前端 `dist` → 由 FastAPI 托管静态页面与 API。

```bash
docker compose up -d --build
```

默认映射：`8800:8800`

数据持久化（Docker volume）
- SQLite：`/data/app.db`
- JWT 密钥：`/data/secret_key`

## EA 接入（MT4/MT5）

### 1) 生成 API Key

Web 登录后进入 “API Key” 页面创建 Key（EA 用 `X-API-Key` 鉴权同步数据）。

### 2) 配置 EA

EA 参数（两端一致）
- `InpServerUrl`：后端基地址，例如：
  - 同机：`http://127.0.0.1:8800`
  - 局域网：`http://192.168.x.x:8800`
- `InpApiKey`：Web 页面生成的 Key

MT5 额外要求
- Tools → Options → Expert Advisors → Allow WebRequest for listed URL
- 把 `InpServerUrl` 加入白名单

## 找回密码（SMTP）

后端提供：
- `POST /api/v1/auth/forgot-password` 发送重置邮件
- `POST /api/v1/auth/reset-password` 使用 token 重置密码

配置位置：`api/.env`
- `SMTP_HOST`
- `SMTP_PORT`（587 常用）
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`（建议与 username 同邮箱）
- `SMTP_STARTTLS=true/false`
- `SMTP_SSL=true/false`（465 常用）
- `PUBLIC_WEB_URL`（邮件里生成重置链接用的 Web 地址）

Gmail 注意事项
- 如果用 Gmail SMTP，通常需要开启 2FA 并使用 App Password。

## 备份与恢复（Linux Docker）

只需要备份 volume（包含 `app.db` 与 `secret_key`）。

备份（生成 tar.gz）
```bash
docker compose down && ts=$(date +%Y%m%d_%H%M%S) && docker run --rm -v traderw_traderw_api_data:/data -v "$PWD":/backup alpine sh -c "cd /data && tar -czf /backup/backup_traderw_${ts}.tar.gz ."
```

恢复（覆盖 volume 内容）
```bash
docker compose down && docker run --rm -v traderw_traderw_api_data:/data -v "$PWD":/backup alpine sh -c "rm -rf /data/* && tar -xzf /backup/备份文件.tar.gz -C /data" && docker compose up -d
```

## 常见问题

### 1) “昨天能登录，今天密码不对”
- 先确认后端启动日志打印的 `DATABASE_URL=...` 是否指向同一个 `app.db`
- 本机直跑默认使用 `api/app.db`；Docker 部署默认使用 volume 内 `/data/app.db`

### 2) 找回密码邮件收不到
- 先看发件箱是否有发送记录
- 再检查垃圾邮件/拦截规则
- Gmail 常见原因：没用 App Password
