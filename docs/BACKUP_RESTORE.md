## 备份与恢复（Linux Docker）

备份对象是 Docker volume（包含 `app.db` 与 `secret_key`）。

### 备份

在 `docker-compose.yml` 同目录执行（生成 `backup_traderw_YYYYMMDD_HHMMSS.tar.gz`）：

```bash
docker compose down && ts=$(date +%Y%m%d_%H%M%S) && docker run --rm -v traderw_traderw_api_data:/data -v "$PWD":/backup alpine sh -c "cd /data && tar -czf /backup/backup_traderw_${ts}.tar.gz ."
```

### 恢复

把 `备份文件.tar.gz` 替换为你的文件名：

```bash
docker compose down && docker run --rm -v traderw_traderw_api_data:/data -v "$PWD":/backup alpine sh -c "rm -rf /data/* && tar -xzf /backup/备份文件.tar.gz -C /data" && docker compose up -d
```

### 注意事项

- volume 名可能因 compose 项目名不同而变化。找不到时先执行：
  - `docker volume ls`
  - 找到包含 `api_data` 的那个 volume 名再替换命令中的 `traderw_traderw_api_data`
