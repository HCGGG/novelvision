#!/usr/bin/env python3
"""
NovelVision 最小演示
在 Windows 上运行：python run_demo.py
功能：生成一张示例图像、一段示例语音、合成一个短视频
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.image_gen import ImageGenWorker
from core.tts import TTSWorker
from core.video_composer import VideoComposerWorker
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop

def print_status(msg):
    print(f"[*] {msg}")

def main():
    print_status("NovelVision 最小演示开始")
    
    # 检查 FFmpeg
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        print_status("✓ FFmpeg 可用")
    except:
        print_status("✗ 未找到 FFmpeg，请先安装并添加到 PATH")
        input("\n按回车退出...")
        return
    
    # 检查火山引擎 API Key
    config_path = os.path.expanduser("~/.openclaw/models.json")
    if not os.path.exists(config_path):
        print_status("✗ 未找到配置文件 ~/.openclaw/models.json")
        print("    请先配置火山引擎 API Key，或使用模型凭据管理工具。")
        input("\n按回车退出...")
        return
    print_status("✓ 配置文件存在")
    
    # 图像生成
    print_status("开始生成图像...")
    image_worker = ImageGenWorker("一个二次元风格的少女，长发，穿着古装，背景是桃花树", max_retries=2)
    loop = QEventLoop()
    image_worker.signals.finished.connect(lambda path: loop.quit())
    image_worker.signals.error.connect(lambda err: (print(f"图像生成错误: {err}"), loop.quit()))
    image_worker.start()
    loop.exec_()
    
    if not image_worker.image_path or not os.path.exists(image_worker.image_path):
        print_status("✗ 图像生成失败")
        input("\n按回车退出...")
        return
    print_status(f"✓ 图像生成完成: {image_worker.image_path}")
    
    # 语音合成
    print_status("开始生成语音...")
    tts_worker = TTSWorker("欢迎使用 NovelVision，这是一款由火山引擎驱动的小说人物视频生成器。", max_retries=2)
    loop = QEventLoop()
    tts_worker.signals.finished.connect(lambda path: loop.quit())
    tts_worker.signals.error.connect(lambda err: (print(f"TTS 错误: {err}"), loop.quit()))
    tts_worker.start()
    loop.exec_()
    
    if not tts_worker.audio_path or not os.path.exists(tts_worker.audio_path):
        print_status("✗ 语音生成失败")
        input("\n按回车退出...")
        return
    print_status(f"✓ 语音生成完成: {tts_worker.audio_path}")
    
    # 视频合成
    print_status("开始合成视频...")
    video_worker = VideoComposerWorker(
        image_paths=[image_worker.image_path],
        audio_paths=[tts_worker.audio_path],
        resolution="1280x720",
        fps=24,
        max_retries=2
    )
    loop = QEventLoop()
    video_worker.signals.finished.connect(lambda path: loop.quit())
    video_worker.signals.error.connect(lambda err: (print(f"视频合成错误: {err}"), loop.quit()))
    video_worker.start()
    loop.exec_()
    
    if not video_worker.output_path or not os.path.exists(video_worker.output_path):
        print_status("✗ 视频合成失败")
        input("\n按回车退出...")
        return
    print_status(f"✓ 视频合成完成: {video_worker.output_path}")
    
    print_status("演示完成！输出文件:")
    print(f"  视频: {video_worker.output_path}")
    print(f"  图像: {image_worker.image_path}")
    print(f"  音频: {tts_worker.audio_path}")
    input("\n按回车退出...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main()