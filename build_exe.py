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
    for folder in ["build", "dist", "NovelVision"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # PyInstaller 配置
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),  # 资源文件
        ('../requirements.txt', '.'),  # 依赖列表
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'requests',
        'PIL',
        'ffmpeg',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NovelVision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico' if os.path.exists('resources/icon.ico') else None,
)
"""
    
    with open("NovelVision.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("正在使用 PyInstaller 打包...")
    try:
        # 检查 ffmpeg 是否安装
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("警告: FFmpeg 未找到。请确保 FFmpeg 已安装并添加到 PATH。")
            print("安装 FFmpeg: https://ffmpeg.org/download.html")
        
        # 执行打包
        subprocess.check_call([sys.executable, "-m", "PyInstaller", "--onefile", "main.py"])
        
        # 输出可执行文件路径
        exe_path = os.path.join("dist", "NovelVision.exe")
        if os.path.exists(exe_path):
            print(f"\n✅ 打包成功: {exe_path}")
            print(f"文件大小: {os.path.getsize(exe_path) / 1024 / 1024:.2f} MB")
            
            # 创建 NSIS 安装脚本
            create_nsis_script()
        else:
            print("❌ 打包失败，未找到生成的可执行文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包过程出错: {e}")
        return False
    return True

def create_nsis_script():
    """创建 NSIS 安装脚本"""
    nsis_content = """; NSIS 安装脚本
SetCompressor lzma
OutFile "NovelVision-Setup.exe"
InstallDir "$PROGRAMFILES\\\\NovelVision"
InstallDirRegKey HKLM "Software\\\\NovelVision" ""

; 页面
Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

; 安装部分
Section "Install"
    SetOutPath "$INSTDIR"
    ; 复制可执行文件
    File /oname=NovelVision.exe "$%O片APP%BUILD%%DIST%NovelVision.exe"
    
    ; 创建快捷方式
    CreateShortcut "$DESKTOP\\\\NovelVision.lnk" "$INSTDIR\\\\NovelVision.exe"
    CreateShortcut "$SMPROGRAMS\\\\NovelVision\\\\NovelVision.lnk" "$INSTDIR\\\\NovelVision.exe"
    
    ; 写入注册表
    WriteRegStr HKLM "Software\\\\NovelVision" "" $INSTDIR
    WriteUninstaller "$INSTDIR\\\\Uninstall.exe"
SectionEnd

; 卸载部分
Section "Uninstall"
    Delete "$INSTDIR\\\\NovelVision.exe"
    Delete "$INSTDIR\\\\Uninstall.exe"
    Delete "$DESKTOP\\\\NovelVision.lnk"
    Delete "$SMPROGRAMS\\\\NovelVision\\\\NovelVision.lnk"
    RMDir "$SMPROGRAMS\\\\NovelVision"
    RMDir "$INSTDIR"
    DeleteRegKey HKLM "Software\\\\NovelVision"
SectionEnd
"""
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_content)
    
    print("✅ NSIS 安装脚本已创建: installer.nsi")
    print("请使用 makensis.exe 编译: makensis installer.nsi")

if __name__ == "__main__":
    build_exe()