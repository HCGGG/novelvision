# NovelVision Pro

一款基于火山引擎 AI 的小说人物视频生成器（Windows 桌面应用）。

## 功能亮点
- 🎨 **AI 图像生成**：根据文字描述自动生成二次元/动漫风格人物图
- 🗣️ **AI 语音合成**：将小说对话/旁白转为自然语音
- 🎬 **视频自动合成**：将图像序列与语音合成为 MP4 视频
- ⚙️ **工作流编排**：一键完成从文本到视频的全流程
- ⚙️ **配置管理**：支持 API Key、分辨率、帧率、语音角色等设置
- 📦 **Windows 安装包**：单文件 exe + 安装向导，即装即用

## 技术栈
- **前端**：PyQt5（简洁桌面界面）
- **后端**：Python 3.10+
- **AI 服务**：火山引擎图像生成 & TTS
- **视频处理**：FFmpeg（内置便携版）
- **打包**：PyInstaller + NSIS

## 快速开始

### 1. 获取程序
下载最新 `NovelVision-Setup.exe` 或 `NovelVision.exe` 从 [Releases](https://github.com/HCGGG/novelvision/releases) 或 Actions Artifacts。

### 2. 安装/运行
- 运行 `NovelVision-Setup.exe` 完成安装，或直接运行 `NovelVision.exe`
- 首次运行会提示配置火山引擎 API Key

### 3. 配置 API Key
点击菜单栏 `⚙️ 设置`，输入火山引擎 API Key。也可在设置中调整分辨率、FPS、语音角色等。

### 4. 创建项目
1. 输入项目名称
2. 点击 `➕ 添加角色`，描述角色外貌、服装、性格等
3. 点击 `➕ 添加场景`，输入场景描述与旁白

### 5. 生成视频
点击 `▶️ 开始生成`，程序将自动执行：
1. 生成场景图像
2. 生成语音
3. 合成视频
4. 完成后在输出目录查看结果

## 内置 FFmpeg
程序已内置 FFmpeg 便携版，无需额外安装。但仍需确保系统可访问视频解码器（Windows 自带）。

## 系统要求
- Windows 10/11 (64-bit)
- 无需安装 Python 或 FFmpeg（运行时完全独立）

## 界面概述

### 主界面
- **左侧面板**：项目管理、角色设定、角色描述
- **右侧面板**：工作流状态、场景列表、预览区域、日志
- **工具栏**：新建、保存、加载、设置、开始/停止生成、关于

### 设置界面
- **API Key**：火山引擎服务凭据
- **输出目录**：生成视频的保存位置
- **分辨率/帧率**：视频参数
- **语音角色**：选择不同 AI 语音

### 关于对话框
显示版本号、构建编号和 Git commit 短哈希。

## 目录结构
```
novelvision/
├── main.py              # 程序入口
├── gui.py               # 主界面
├── settings.py          # 配置管理
├── settings_dialog.py   # 设置对话框
├── build_exe.py         # 打包脚本
├── requirements.txt     # Python 依赖
├── BUILD.md            # 构建指南（开发者）
├── README.md           # 使用说明
├── core/               # 核心模块
│   ├── image_gen.py    # 图像生成
│   ├── tts.py         # 语音合成
│   ├── video_composer.py # 视频合成（内置FFmpeg查找）
│   └── workflow.py    # 工作流管理
├── .github/workflows/  # GitHub Actions
│   └── build-windows.yml
├── vendor/             # 第三方便携二进制
│   └── ffmpeg/        # 放置 ffmpeg.exe, ffprobe.exe（开发者使用）
└── config.json         # 用户配置（自动创建）
```

## 构建说明（开发者）

### 本地构建
```cmd
git clone git@github.com:HCGGG/novelvision.git
cd novelvision
pip install -r requirements.txt
python build_exe.py
```
生成 `dist/NovelVision.exe`。如需内置 FFmpeg，请先下载 `ffmpeg.exe` 和 `ffprobe.exe` 到 `vendor/ffmpeg/`。

### GitHub Actions
推送至 main 分支会自动触发 Windows 构建，Artifact 可在 Actions 页面下载。

## 常见问题

### Q: 启动时报错 "ffmpeg 未安装"
A: 如果使用从 GitHub 下载的 exe，应该已内置 FFmpeg。如果从源码运行，请确保 FFmpeg 在 PATH 或 `vendor/ffmpeg/` 目录。

### Q: API Key 配置后无效
A: 检查网络连接，确认火山引擎服务已开通，API Key 正确。服务可能需白名单或开启代理。

### Q: 视频生成失败
A: 检查日志输出。可能原因：图片生成失败（API 问题）、音频合成失败、FFmpeg 错误。确保有足够磁盘空间。

### Q: 如何确认版本
A: 点击菜单 `ℹ️ 关于`，查看构建编号和 commit 短哈希。确保下载的是最新构建。

## 许可证
本项目为演示用途，AI 服务需自行申请火山引擎配额。

## 支持与反馈
如有问题请提交 issue，或联系开发者。