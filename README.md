# NovelVision Pro

一款基于火山引擎 AI 的小说人物视频生成器（Windows 桌面应用）。

## 功能亮点
- 🎨 **AI 图像生成**：根据文字描述自动生成二次元/动漫风格人物图
- 🗣️ **AI 语音合成**：将小说对话/旁白转为自然语音
- 🎬 **视频自动合成**：将图像序列与语音合成为 MP4 视频
- ⚙️ **工作流编排**：一键完成从文本到视频的全流程
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
创建 `config.json`（或使用 `~/.openclaw/models.json`）：
```json
{
  "models": [
    {
      "provider": "volcengine",
      "api_key": "你的API_KEY"
    }
  ]
}
```

### 3. 运行演示
```cmd
python run_demo.py
```
演示将生成一张图、一段语音并合成一个短视频。

### 4. 构建 Windows 安装包
参见 [BUILD.md](BUILD.md) 详细步骤。

## 使用说明

1. **项目/角色管理**
   - 新建项目，输入角色描述（外貌、性格、服装等）
   - 点击“生成图像”预览效果
   - 添加场景，输入场景描述与旁白

2. **工作流**
   - 点击“开始生成”自动执行：图像 → 语音 → 视频
   - 进度条实时显示状态
   - 完成后可导出视频和项目文件

3. **输出**
   - 视频保存在 `output/` 目录
   - 项目文件 `.nvproj` 可二次编辑

## 系统要求
- Windows 10/11 (64-bit)
- Python 3.10+（开发者）
- FFmpeg（视频处理）

## 打包说明
运行 `python build_exe.py` 生成 `dist/NovelVision.exe`，再用 NSIS 编译 `installer.nsi` 得到安装包。

## 许可证
本项目为演示用途，AI 服务需自行申请火山引擎配额。

## 支持与反馈
如有问题请提交 issue，或联系开发者。