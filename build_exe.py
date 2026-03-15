#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

# 修复 Windows 控制台中文编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def build_exe():
    """使用 PyInstaller 打包 NovelVision"""
    
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 检查是否已安装 PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller==6.10.0"])
    
    # 清理之前的构建
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    print("正在使用 PyInstaller 打包...")
    try:
        # 检查 ffmpeg 是否安装
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("警告: FFmpeg 未找到。请确保 FFmpeg 已安装并添加到 PATH。")
            print("安装 FFmpeg: https://ffmpeg.org/download.html")
        
        # 执行打包，指定输出名称
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--name", "NovelVision",
            "main.py"
        ])
        
        # 输出可执行文件路径
        exe_path = os.path.join("dist", "NovelVision.exe")
        if os.path.exists(exe_path):
            print(f"\n✅ 打包成功: {exe_path}")
            print(f"文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
        else:
            print("❌ 打包失败，未找到生成的可执行文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包过程出错: {e}")
        return False
    return True

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)