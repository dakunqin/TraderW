## MT5 EA（TraderW_Relay.mq5）

### 1) 功能
- 定时通过 WebRequest 上报：当前账号信息 + 当前挂单（Orders）+ 当前持仓（Positions）
- 定时拉取服务端指令（close），在本机 MT5 上执行：
  - target_kind=position：平仓
  - target_kind=order：撤单
- 执行完成后回传结果到服务端

### 2) 在 MT5 中使用
1. 将 [TraderW_Relay.mq5](file:///e:/EAs/TraderW/ea/TraderW_Relay.mq5) 放到 `MQL5/Experts/` 后编译
2. 在图表加载 EA，填写输入参数：
   - `InpServerUrl`：例如 `http://127.0.0.1:8000`
   - `InpApiKey`：在 Web 控制台生成的 Key
3. 在 MT5：`Tools -> Options -> Expert Advisors` 中，把 `InpServerUrl` 对应的域名/地址加入 “允许 WebRequest 的 URL 列表”
4. 确认终端日志无报错，Web 控制台能看到该 MT5 账号数据

### 3) 服务端接口约定
- 同步：`POST {InpServerUrl}/api/v1/mt5/sync`，Header：`X-API-Key: <key>`
- 拉指令：`GET {InpServerUrl}/api/v1/mt5/actions?mt5_login=...&mt5_server=...`
- 回执：`POST {InpServerUrl}/api/v1/mt5/action-results`

## MT4 EA（TraderW_Relay_MT4.mq4）

### 1) 功能
- 定时通过 WebRequest 上报：当前账号信息 + 当前挂单（Orders）+ 当前持仓（Positions）
- 定时拉取服务端指令（close），在本机 MT4 上执行：
  - target_kind=position：对 OP_BUY/OP_SELL 进行 OrderClose
  - target_kind=order：对挂单进行 OrderDelete
- 执行完成后回传结果到服务端

### 2) 在 MT4 中使用
1. 将 [TraderW_Relay_MT4.mq4](file:///e:/EAs/TraderW/ea/TraderW_Relay_MT4.mq4) 放到 `MQL4/Experts/` 后编译
2. 在图表加载 EA，填写输入参数：
   - `InpServerUrl`：例如 `http://127.0.0.1:8000` 或 `http://192.168.0.68:8000`
   - `InpApiKey`：在 Web 控制台生成的 Key
3. 在 MT4：`Tools -> Options -> Expert Advisors` 中，把 `InpServerUrl` 对应的域名/地址加入 “允许 WebRequest 的 URL 列表”

