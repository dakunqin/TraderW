## 微信小程序（最简单方案：WebView 壳）

目标：用最少开发量，把现有 Web 站点嵌入到小程序中访问。

本仓库已提供一个最小小程序壳工程：`miniprogram/`，打开后直接加载：
- `https://traderw.yiyideyi.org/?from=wxapp`

### 1) 前置条件

- 已有个人微信开发者账号
- 域名必须为 HTTPS 且证书有效（你的域名已满足：`https://traderw.yiyideyi.org/`）
- Web 页面在小程序 WebView 中不能强制跳转到未备案/未加入白名单的域名

### 2) 配置域名白名单（必须）

微信公众平台 → 小程序 → 开发 → 开发管理 → 开发设置：

- 业务域名（WebView 域名）：添加
  - `traderw.yiyideyi.org`

说明：
- 这里是给 `<web-view>` 用的域名白名单，必须配置，否则小程序打不开网页。
- 只需要填域名，不需要路径。

### 3) 用微信开发者工具打开项目

1. 打开微信开发者工具
2. 导入项目
3. 项目目录选择仓库根目录（包含 `miniprogram/project.config.json` 的目录）
4. 把 `miniprogram/project.config.json` 里的 `appid` 替换为你自己的 AppID

### 4) 代码说明（无需改动即可运行）

- 小程序入口：`miniprogram/app.json`
- 页面：`miniprogram/pages/web/web`
- WebView：`miniprogram/pages/web/web.wxml`

### 5) 发布流程（概要）

1. 开发者工具上传代码
2. 微信公众平台提交审核
3. 审核通过后发布

### 6) 常见问题

#### A) 打不开网页 / 白屏
- 检查是否已配置 “业务域名”
- 检查域名是否 HTTPS、证书是否完整可信
- 检查站点是否重定向到其它域名（若有，需要把目标域名也加到业务域名）

#### B) 登录后接口请求失败
如果你的前端构建时固定了 `VITE_API_BASE=http://127.0.0.1:8800`，在小程序 WebView（以及任何外网访问）都会请求到客户端本机，导致 `Failed to fetch`。

建议：
- 部署环境不要设置 `VITE_API_BASE`，让前端自动跟随当前域名同源访问 `/api/...`

#### C) 需要原生能力（扫码/分享/订阅消息）
当前方案只是 WebView 外壳。若需要小程序原生能力，需要把关键页面改为原生小程序页面，并通过后端 API 提供数据。
