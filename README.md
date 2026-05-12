# VideoMind

一个本地运行的跨平台视频下载与 AI 总结工作台，支持：

- B站
- YouTube
- TikTok
- 抖音

当前 MVP 包含：

- 链接自动识别与视频元信息解析
- 视频、音频、字幕、封面下载
- 本地任务状态展示
- 基于字幕的 AI 总结
- 本地设置管理

## 技术栈

- 前端：React + TypeScript + Vite
- 后端：FastAPI
- 下载引擎：yt-dlp
- AI 接口：兼容 OpenAI 风格的聊天补全接口

## 快速启动

### 1. 安装前端依赖

```bash
npm install
```

### 2. 安装后端依赖

```bash
python -m pip install -r requirements.txt
```

### 3. 安装 yt-dlp

请先确保本机已安装 `yt-dlp`，否则解析与下载接口会返回错误。

### 4. 启动后端

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 启动前端

```bash
npm run dev -- --host 0.0.0.0 --port 5173
```

前端开发环境已通过 `vite` 代理将 `/api` 请求转发到 `http://127.0.0.1:8000`。

## 测试命令

```bash
npm run check
npm run lint
npm test
python -m pytest api/tests
```

## B站 412 说明

- 如果 B站 返回 `HTTP Error 412: Precondition Failed`，通常是平台风控校验触发
- 请打开设置页，填写 `浏览器 Cookie 来源`
- 推荐值：
  - `chrome`
  - `edge`
  - `firefox`
  - `chrome:Default`
- 填写前请确保对应浏览器里已经登录 B站
- 也可以改用 `Cookie 文件路径`，填写 Netscape 格式 `cookies.txt` 的绝对路径

## 文档

- 设计文档：`docs/superpowers/specs/2026-05-12-video-downloader-design.md`
- PRD：`.trae/documents/video-downloader-prd.md`
- 技术架构：`.trae/documents/video-downloader-architecture.md`
