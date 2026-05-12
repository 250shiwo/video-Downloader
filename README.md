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
- B站 普通公开视频原生解析与下载

## 技术栈

- 前端：React + TypeScript + Vite
- 后端：FastAPI
- 下载引擎：B站 原生下载通道 + yt-dlp
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

## B站 说明

- 对普通公开 `B站` 视频，后端优先走站内公开接口解析元信息和播放流
- 下载视频时会分别获取音视频流，并通过 `ffmpeg` 合并为本地文件
- 若链接属于会员、番剧、付费、区域限制或其他受限内容，系统会返回用户可理解的失败提示

## 文档

- 设计文档：`docs/superpowers/specs/2026-05-12-video-downloader-design.md`
- PRD：`.trae/documents/video-downloader-prd.md`
- 技术架构：`.trae/documents/video-downloader-architecture.md`
