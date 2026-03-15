#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
import json
from PyQt5.QtCore import QThread, pyqtSignal
import tempfile
import json

class VideoComposerWorker(QThread):
    signals = pyqtSignal(str, str)  # finished(video_path), error(error_msg)
    
    def __init__(self, image_paths, audio_paths, output_path=None, resolution="1920x1080", fps=30, max_retries=3):
        super().__init__()
        self.image_paths = image_paths
        self.audio_paths = audio_paths
        self.output_path = output_path or self.default_output_path()
        self.resolution = resolution
        self.fps = fps
        self.max_retries = max_retries
        
    def run(self):
        attempt = 0
        while attempt <= self.max_retries:
            try:
                if attempt > 0:
                    time.sleep(2 ** attempt)  # 指数退避: 2s, 4s
                    
                # 检查 FFmpeg 是否可用
                ffmpeg_path = self.find_ffmpeg()
                if not ffmpeg_path:
                    self.signals.error.emit("未找到 FFmpeg，请安装 FFmpeg 或将 ffmpeg.exe 放入 vendor/ffmpeg/ 目录")
                    return
                
                # 1. 将图片序列转换为视频片段
                video_segments = []
                for i, img_path in enumerate(self.image_paths):
                    seg_path = self.create_image_segment(img_path, duration=3.0, index=i, ffmpeg_path=ffmpeg_path)
                    video_segments.append(seg_path)
                
                # 2. 合并视频片段
                concat_file = self.create_concat_file(video_segments)
                temp_video = self.merge_segments(concat_file, ffmpeg_path)
                
                # 3. 合并音频
                final_audio = self.merge_audio_tracks()
                
                # 4. 合成最终视频
                self.compose_final_video(temp_video, final_audio, ffmpeg_path)
                
                self.signals.finished.emit(self.output_path)
                return
                
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    self.signals.error.emit(f"视频合成错误: {str(e)}")
                    return
                # continue to retry
            
    def find_ffmpeg(self):
        """查找 FFmpeg 可执行文件"""
        # 1. 检查 vendor 目录
        vendor_dir = os.path.join(os.path.dirname(__file__), "../vendor/ffmpeg")
        if os.path.exists(vendor_dir):
            ffmpeg_path = os.path.join(vendor_dir, "ffmpeg.exe")
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        
        # 2. 检查系统 PATH
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=2)
            return "ffmpeg"
        except:
            pass
        
        # 3. 检查常见安装路径
        common_paths = [
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # 4. 检查 PyInstaller 的临时目录
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            ffmpeg_path = os.path.join(base_dir, "ffmpeg.exe")
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        
        return None
    
    def default_output_path(self):
        import tempfile
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(tempfile.gettempdir(), f"novelvision_output_{timestamp}.mp4")
    
    def create_image_segment(self, image_path, duration=3.0, index=0, ffmpeg_path="ffmpeg"):
        """将单张图片转换为视频片段"""
        seg_path = os.path.join(tempfile.gettempdir(), f"seg_{index}.mp4")
        
        cmd = [
            ffmpeg_path, "-y",
            "-loop", "1",
            "-i", image_path,
            "-t", str(duration),
            "-vf", f"scale={self.resolution}:force_original_aspect_ratio=decrease,pad={self.resolution}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", str(self.fps),
            seg_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"创建视频片段失败: {result.stderr}")
            
        return seg_path
    
    def create_concat_file(self, video_segments):
        """创建 ffmpeg concat 文件"""
        concat_txt = os.path.join(tempfile.gettempdir(), "concat.txt")
        with open(concat_txt, "w") as f:
            for seg in video_segments:
                f.write(f"file '{os.path.abspath(seg)}'\n")
        return concat_txt
    
    def merge_segments(self, concat_file, ffmpeg_path="ffmpeg"):
        """合并视频片段"""
        merged = os.path.join(tempfile.gettempdir(), "merged.mp4")
        cmd = [
            ffmpeg_path, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            merged
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"合并片段失败: {result.stderr}")
        return merged
    
    def merge_audio_tracks(self):
        """合并音频轨道"""
        if not self.audio_paths:
            return None
            
        # 使用第一个音频
        return self.audio_paths[0]
    
    def compose_final_video(self, video_input, audio_input, ffmpeg_path="ffmpeg"):
        """合成最终视频"""
        cmd = [
            ffmpeg_path, "-y",
            "-i", video_input,
            "-i", audio_input if audio_input else "anullsrc",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            self.output_path
        ]
        
        if not audio_input:
            cmd = [
                ffmpeg_path, "-y",
                "-i", video_input,
                "-c:v", "copy",
                "-an",
                self.output_path
            ]
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"合成最终视频失败: {result.stderr}")
    
    def get_duration(self, filepath):
        """获取媒体文件时长"""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath],
                capture_output=True, text=True, timeout=10
            )
            return float(result.stdout.strip())
        except:
            return 3.0  # 默认3秒