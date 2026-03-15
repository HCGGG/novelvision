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
- **视频处理**：FFmpeg
- **打包**：PyInstaller + NSIS

## 快速开始

### 1. 安装依赖
```cmd
pip install -r requirements.txt
```
并确保 FFmpeg 已安装并加入 PATH。

### 2. 配置 API Key
运行程序后，点击菜单栏 `⚙️ 设置`，输入火山引擎 API Key。

### 3. 创建项目
1. 输入项目名称
2. 点击 `➕ 添加角色`，描述角色外貌、服装、性格等
3. 点击 `➕ 添加场景`，输入场景描述与旁白

### 4. 生成视频
点击 `▶️ 开始生成`，程序将自动执行：
1. 生成场景图像
2. 生成语音
3. 合成视频

### 5. 构建安装包
参见 [BUILD.md](BUILD.md) 详细步骤。

## 系统要求
- Windows 10/11 (64-bit)
- Python 3.10+（开发者）
- FFmpeg（视频处理）

## 界面概述

### 主界面
- **左侧面板**：项目管理、角色设定、角色描述
- **右侧面板**：工作流状态、场景列表、预览区域、日志
- **工具栏**：新建、保存、加载、设置、开始/停止生成

### 设置界面
- **API Key**：火山引擎服务凭据
- **输出目录**：生成视频的保存位置
- **分辨率/帧率**：视频参数
- **语音角色**：选择不同 AI 语音

## 目录结构
```
novelvision/
├── main.py              # 程序入口
├── gui.py               # 主界面（已更新）
├── settings.py          # 配置管理
├── settings_dialog.py   # 设置对话框
├── build_exe.py         # 打包脚本（已更新）
├── requirements.txt     # Python 依赖
├── BUILD.md            # 构建指南
├── README.md           # 使用说明
├── core/               # 核心模块
│   ├── image_gen.py    # 图像生成
│   ├── tts.py         # 语音合成
│   ├── video_composer.py # 视频合成
│   └── workflow.py    # 工作流管理
├── .github/workflows/  # GitHub Actions
│   └── build-windows.yml
└── config.json         # 用户配置（自动创建）
```

## 配置说明

配置文件保存在 `config.json`（或用户目录 `~/.novelvision/config.json`），包含：

```json
{
  "volcengine_api_key": "你的API_KEY",
  "resolution": "1920x1080",
  "fps": 30,
  "voice": "zh-CN-XiaoxiaoNeural",
  "image_style": "anime",
  "max_retries": 3,
  "output_dir": "output"
}
```

## 常见问题

### Q: 程序启动报错
A: 检查 Python 版本（3.10+），确保 PyQt5 已安装，FFmpeg 可用。

### Q: API Key 配置后无效
A: 检查网络连接，确认火山引擎服务已开通，API Key 正确。

### Q: 视频生成失败
A: 检查 FFmpeg 安装，网络是否通畅，火山引擎配额是否足够。

### Q: 如何构建 exe
A: 运行 `python build_exe.py`，确保所有依赖已安装。

## 开发指南

### 添加功能
- 在 `core/` 目录添加新模块
- 在 `gui.py` 添加界面元素
- 在 `WorkflowManager` 中集成新功能

### 构建发布
1. 确保代码提交到 `main` 分支
2. GitHub Actions 会自动构建并发布 Release
3. 下载 `NovelVision-*.zip` 解压使用

## 许可证
本项目为演示用途，AI 服务需自行申请火山引擎配额。

## 支持与反馈
如有问题请提交 issue，或联系开发者。