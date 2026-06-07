## 部署（Linux Docker）

本项目支持单容器部署：镜像构建时打包前端 `dist`，运行时由 FastAPI 同端口提供页面与 API。

### 1) 上传文件

建议上传整个仓库（不包含 `node_modules/`、`dist/`、`api/.venv/` 等），服务器上执行构建。

### 2) 启动

在 `docker-compose.yml` 同目录执行：

```bash
docker compose up -d --build
```

默认映射端口：`8800:8800`

### 3) 反向代理（主机 Nginx）

你可以把主机 Nginx 反代到 `127.0.0.1:8800`，并统一用一个域名对外提供服务。

### 4) 数据持久化

数据保存在 Docker volume 中：
- `/data/app.db`：SQLite 数据库
- `/data/secret_key`：JWT 密钥（不建议丢失，否则旧 token 失效）

### 5) 升级流程（不丢数据）

```bash
docker compose pull
docker compose up -d --build
```

如遇到 DB 结构变更且不兼容，需要按版本补迁移脚本或按备份/恢复流程回滚。
