## 后端（FastAPI）

### 1) 安装依赖
```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) 配置
可选：在 `api/.env` 中设置
- SMTP（找回密码必需）
  - `SMTP_HOST` / `SMTP_PORT`
  - `SMTP_USERNAME` / `SMTP_PASSWORD`
  - `SMTP_FROM`
  - `SMTP_SSL` / `SMTP_STARTTLS`
  - `PUBLIC_WEB_URL`
- 其他（一般不需要）
  - `SECRET_KEY`：不设置会自动生成并持久化（本机为 `api/.secret_key`，Docker 为 `/data/secret_key`）
  - `DATABASE_URL`：不设置会自动选择（Docker 走 `/data/app.db`，本机走 `api/app.db`）

### 3) 运行
```bash
cd api
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8800
```

### 4) 测试
```bash
cd api
.venv\Scripts\activate
pytest -q
```
