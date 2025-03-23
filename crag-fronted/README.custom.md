# Crag 前端应用

这是 Crag 平台的前端应用，基于 Vue 3、TypeScript 和 Ant Design Vue 构建。

## 功能特性

- GitHub OAuth 登录
- 响应式布局
- 现代化 UI 设计
- 后端 API 集成

## 技术栈

- Vue 3
- TypeScript
- Ant Design Vue
- Vue Router
- Axios

## 开始使用

### 前提条件

- Node.js 16+
- npm 或 yarn

### 安装依赖

```bash
npm install
# 或者
yarn install
```

### 配置环境变量

在根目录创建 `.env` 文件（或修改现有的）:

```
# API 配置
VITE_API_BASE_URL=http://localhost:8000

# GitHub OAuth 配置
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_REDIRECT_URI=http://localhost:5173/auth/github/callback
```

> 注意：你需要在 GitHub 创建一个 OAuth 应用并获取 Client ID。

### 本地开发

```bash
npm run dev
# 或者
yarn dev
```

### 构建生产版本

```bash
npm run build
# 或者
yarn build
```

## 项目结构

```
src/
├── assets/        # 静态资源
├── components/    # 可复用组件
├── router/        # 路由配置
├── services/      # API 服务
├── views/         # 页面视图
├── App.vue        # 根组件
└── main.ts        # 入口文件
```

## GitHub OAuth 认证流程

1. 用户点击 "使用 GitHub 登录" 按钮
2. 重定向到 GitHub 授权页面
3. 用户授权后，GitHub 重定向回应用的回调 URL
4. 前端获取授权码，发送到后端交换令牌
5. 使用令牌获取用户信息并完成登录

## 后端 API 集成

应用设计为与后端 API 集成，以下是主要的 API 端点：

- `/api/auth/github/callback` - 处理 GitHub OAuth 回调
- `/api/user/current` - 获取当前登录用户信息
- `/api/auth/logout` - 登出处理

## 贡献

欢迎贡献代码、报告问题或提出新功能建议。 