## 找回密码（SMTP）

后端接口：
- `POST /api/v1/auth/forgot-password`：输入邮箱，发送重置链接
- `POST /api/v1/auth/reset-password`：输入 token + 新密码，完成重置

前端页面：
- `/forgot-password`
- `/reset-password?token=...`

### 1) 配置文件

创建 `api/.env`（可从 `api/.env.example` 复制）并填写：
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM`
- `SMTP_SSL`
- `SMTP_STARTTLS`
- `PUBLIC_WEB_URL`

### 2) 常用 SMTP 组合

587（常见）
- `SMTP_PORT=587`
- `SMTP_SSL=false`
- `SMTP_STARTTLS=true`

465（常见）
- `SMTP_PORT=465`
- `SMTP_SSL=true`
- `SMTP_STARTTLS=false`

### 3) Gmail 注意事项

如果使用 Gmail SMTP：
- 通常必须开启 2FA
- 使用 App Password 作为 `SMTP_PASSWORD`

### 4) 收不到邮件

常见原因：
- 进垃圾邮件
- `SMTP_FROM` 与真实发件账号不一致
- 邮件服务拦截或延迟
