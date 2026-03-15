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

def generate_version_file():
    """生成 version.py 包含构建信息"""
    try:
        commit = subprocess.check_output(["git", "log", "-1", "--format=%H"], text=True).strip()[:8]
    except:
        commit = "unknown"
    run_number = os.getenv("GITHUB_RUN_NUMBER", "local")
    version_content = f'''# 自动生成的构建信息
BUILD_RUN_NUMBER = "{run_number}"
BUILD_COMMIT_SHA = "{commit}"
'''
    # 确保目录存在
    version_dir = os.path.join("novelvision")
    os.makedirs(version_dir, exist_ok=True)
    version_path = os.path.join(version_dir, "version.py")
    with open(version_path, "w", encoding="utf-8") as f:
        f.write(version_content)
    print(f"[BUILD] Generated version.py: run={run_number}, commit={commit}")

def copy_ffmpeg_binaries():
    """复制 FFmpeg 便携二进制文件到 dist 目录"""
    vendor_dir = os.path.join("vendor", "ffmpeg")
    dist_dir = "dist"
    
    if not os.path.exists(vendor_dir):
        print(f"[WARN] vendor/ffmpeg/ 目录不存在，跳过复制")
        return
    
    binaries = ["ffmpeg.exe", "ffprobe.exe"]
    for binary in binaries:
        src = os.path.join(vendor_dir, binary)
        if os.path.exists(src):
            shutil.copy2(src, dist_dir)
            print(f"[BUILD] 复制 {binary} 到 dist/")
        else:
            print(f"[WARN] 未找到 {binary} 在 vendor/ffmpeg/")

def build_exe():
    """使用 PyInstaller 打包 NovelVision"""
    
    # 确保在项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # 生成版本信息文件
    generate_version_file()
    
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
            print(f"已清理: {folder}/")
    
    print("正在使用 PyInstaller 打包...")
    try:
        # 检查 ffmpeg 是否安装（用于构建时验证）
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            print("FFmpeg: ✓ 系统可用")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("警告: 系统未找到 FFmpeg，将使用内置便携版（如果提供）")
        
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
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"\n✅ 打包成功: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")
            
            # 复制 FFmpeg 二进制文件
            copy_ffmpeg_binaries()
            
            # 列出 dist 目录内容
            print("\n📦 dist/ 目录内容:")
            for item in os.listdir(dist_dir):
                print(f"  - {item}")
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