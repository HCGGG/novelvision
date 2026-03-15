# NovelVision Pro - Windows 构建指南

## 概述
本指南面向 Windows 开发者/用户，指导如何从源代码构建 `NovelVision Pro` 的单文件安装包（`.exe` + NSIS 安装器）。

## 前置要求

### 1. Python 环境
- 安装 Python 3.10+（建议 3.11 或 3.12）
- 确保 `python` 和 `pip` 在系统 PATH 中
- 验证安装：
  ```cmd
  python --version
  pip --version
  ```

### 2. 依赖工具
- **FFmpeg**：视频处理
  - 下载地址：https://ffmpeg.org/download.html → Windows builds（推荐 gyan.dev）
  - 解压后将 `bin` 目录添加到 PATH
  - 测试：`ffmpeg -version`
- **NSIS**（Nullsoft Scriptable Install System）：制作安装包
  - 下载：https://nsis.sourceforge.io/Download
  - 安装后确保 `makensis.exe` 在 PATH 中
  - 测试：`makensis /VERSION`

### 3. 火山引擎 API Key
- 在火山引擎控制台创建并开通图像生成、TTS 服务
- 将 API Key 保存到 `~/.openclaw/models.json`（或同目录 `config.json`），格式：
  ```json
  {
    "models": [
      {
        "provider": "volcengine",
        "api_key": "你的_API_KEY"
      }
    ]
  }
  ```

## 构建步骤

### 步骤 1: 克隆或获取源代码
将 `novelvision` 文件夹放置到你希望的项目目录，例如 `C:\Projects\novelvision\`

### 步骤 2: 安装 Python 依赖
```cmd
cd C:\Projects\novelvision
pip install -r requirements.txt
```
这将安装：PyQt5, requests, Pillow, ffmpeg-python 等。

### 步骤 3: 测试运行演示（可选）
```cmd
python run_demo.py
```
该脚本会依次测试：
- 火山引擎图像生成
- 火山引擎 TTS
- FFmpeg 视频合成

如果全部成功，会生成一个示例视频 `output/` 目录下。

### 步骤 4: 使用 PyInstaller 打包
```cmd
python build_exe.py
```
或手动：
```cmd
pyinstaller --onefile main.py --name NovelVision
```

打包完成后，`dist/NovelVision.exe` 即为单文件可执行程序。

### 步骤 5: 创建安装包
1. 确保可执行文件 `NovelVision.exe` 在 `dist/` 目录
2. 运行 NSIS 编译安装脚本：
   ```cmd
   makensis installer.nsi
   ```
   （需要提前修改 installer.nsi 中的路径）
3. 生成的 `NovelVision-Setup.exe` 即为安装包

### 步骤 6: 分发与测试
在干净的 Windows 虚拟机或测试机上运行安装包，验证：
- 安装过程正常
- 桌面快捷方式和开始菜单项创建
- 程序启动正常
- 功能区（生成图像、语音、视频）可用

## 目录结构
```
novelvision/
├── main.py              # 程序入口
├── gui.py               # 主界面
├── run_demo.py          # 演示脚本
├── build_exe.py         # 打包脚本
├── requirements.txt     # Python 依赖
├── installer.nsi        # NSIS 安装脚本
├── core/                # 核心模块
│   ├── image_gen.py
│   ├── tts.py
│   ├── video_composer.py
│   └── workflow.py
├── resources/           # 图标、素材（可选）
└── output/              # 输出目录（运行中生成）
```

## 常见问题

### Q: 打包后程序启动报错“找不到 PyQt5”
A: 确保 PyInstaller 正确打包了所有隐藏导入。可尝试手动指定 `--hiddenimport PyQt5.sip`。

### Q: FFmpeg 找不到
A: 有两种方案：
1. 安装系统级 FFmpeg 并添加到 PATH（推荐）
2. 将 FFmpeg 的 `ffmpeg.exe` 和 `ffprobe.exe` 复制到 `dist/` 目录，程序会自动使用同目录下的可执行文件

### Q: 火山引擎 API 调用失败
A: 检查：
- API Key 是否正确
- 网络是否可达（可能需要代理）
- 是否已开通对应服务（图像生成、TTS）

### Q: 安装包体积过大
A: 单文件 PyInstaller 打包会包含所有依赖。可使用 `--exclude-module` 排除未使用模块，或考虑便携版（不打包为单文件）。

## 后续优化
- 添加配置界面（设置 API Key、默认分辨率等）
- 支持批量生成（多场景）
- 更多视频特效与转场
- 多语言界面

## 联系与反馈
如有问题，请提交 issue 或联系开发。

---
**祝构建顺利！**