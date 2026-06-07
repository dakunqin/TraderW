## 1. 架构设计

```mermaid
flowchart LR
  subgraph FE["前端（Web 控制台）"]
    A["React 应用（Dashboard）"]
  end
  subgraph BE["后端（Python Web 服务）"]
    B["FastAPI（Auth/API/EA 接入）"]
    C["业务服务层（同步/指令/审计）"]
    D["数据访问层（SQLAlchemy）"]
  end
  subgraph DB["数据层"]
    E["SQLite（可替换为 PostgreSQL）"]
  end
  subgraph EA["MT5 端"]
    F["EA（MQL5）WebRequest 客户端"]
  end
  A -->|HTTPS JSON| B
  F -->|HTTPS JSON（API Key）| B
  B --> C --> D --> E
```

## 2. 技术选型说明
- 前端：React@18 + TypeScript + Vite + TailwindCSS
- 后端：Python + FastAPI + Uvicorn
- 认证：Web 使用 JWT（access token + refresh token）；EA 使用 API Key（仅用于 EA 接口）
- 数据库：SQLite（开发默认），可配置为 PostgreSQL
- 部署：单机部署（前端静态资源 + FastAPI），HTTPS 由反向代理（如 Nginx/Caddy）负责

## 3. 路由定义（前端页面）
| Route | 用途 |
|------|------|
| /login | 登录 |
| /register | 注册 |
| /dashboard | 概览 |
| /api-keys | API Key 管理 |
| /mt5-accounts | MT5 账号列表 |
| /mt5-accounts/:id | MT5 账号详情（订单/持仓） |

## 4. API 定义（后端）

### 4.1 认证与用户
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- GET /api/v1/me

### 4.2 API Key 管理（登录态）
- GET /api/v1/api-keys
- POST /api/v1/api-keys
- POST /api/v1/api-keys/{id}/disable
- DELETE /api/v1/api-keys/{id}

### 4.3 EA 接入（API Key 鉴权）
- POST /api/v1/mt5/sync
  - 请求：{ mt5_account: {...}, positions: [...], orders: [...], sent_at }
  - 返回：{ ok: true }
- GET /api/v1/mt5/actions
  - 查询参数：mt5_login, mt5_server
  - 返回：{ actions: [ { id, type:"close", ticket, symbol, volume, requested_at } ] }
- POST /api/v1/mt5/action-results
  - 请求：{ action_id, status:"success"|"failed", error_code?, error_message?, executed_at }
  - 返回：{ ok: true }

### 4.4 订单与平仓（登录态）
- GET /api/v1/mt5-accounts
- GET /api/v1/mt5-accounts/{id}/orders
- GET /api/v1/mt5-accounts/{id}/positions
- POST /api/v1/orders/{order_id}/close
  - 行为：创建待执行 close 指令（不直接在服务端平仓）

## 5. 服务端分层结构图

```mermaid
flowchart TD
  A["API Router（FastAPI）"] --> B["Service（业务服务）"]
  B --> C["Repository（数据访问）"]
  C --> D["DB（SQLite/PostgreSQL）"]
```

## 6. 数据模型

### 6.1 ER 图
```mermaid
erDiagram
  USER ||--o{ API_KEY : owns
  USER ||--o{ MT5_ACCOUNT : owns
  MT5_ACCOUNT ||--o{ MT5_ORDER : has
  MT5_ACCOUNT ||--o{ MT5_POSITION : has
  USER ||--o{ ACTION : requests
  MT5_ACCOUNT ||--o{ ACTION : targets
  ACTION ||--o{ ACTION_RESULT : has

  USER {
    int id
    string email
    string password_hash
    datetime created_at
  }
  API_KEY {
    int id
    int user_id
    string key_hash
    string prefix
    bool is_active
    datetime created_at
    datetime last_used_at
  }
  MT5_ACCOUNT {
    int id
    int user_id
    string mt5_login
    string mt5_server
    string mt5_company
    string currency
    float balance
    float equity
    float margin
    datetime last_sync_at
  }
  MT5_ORDER {
    int id
    int mt5_account_id
    long ticket
    string symbol
    string type
    float volume
    float price_open
    float sl
    float tp
    datetime time_setup
    datetime time_done
    datetime updated_at
  }
  MT5_POSITION {
    int id
    int mt5_account_id
    long ticket
    string symbol
    string type
    float volume
    float price_open
    float sl
    float tp
    float profit
    datetime time_open
    datetime updated_at
  }
  ACTION {
    int id
    int user_id
    int mt5_account_id
    string type
    long ticket
    string status
    datetime requested_at
  }
  ACTION_RESULT {
    int id
    int action_id
    string status
    int error_code
    string error_message
    datetime executed_at
  }
```

### 6.2 DDL（逻辑层）
后续实现以 ORM 迁移生成（Alembic），并添加索引：
- api_key(prefix)、mt5_account(user_id, mt5_login, mt5_server)、order(ticket)、position(ticket)、action(status, mt5_account_id)

