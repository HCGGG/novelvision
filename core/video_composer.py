#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
import json
from PyQt5.QtCore import QThread, pyqtSignal
import time

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
                if not self.check_ffmpeg():
                    self.signals.error.emit("未找到 FFmpeg，请安装 FFmpeg 并添加到 PATH")
                    return
                
                # 1. 将图片序列转换为视频片段
                video_segments = []
                for i, img_path in enumerate(self.image_paths):
                    seg_path = self.create_image_segment(img_path, duration=3.0, index=i)
                    video_segments.append(seg_path)
                
                # 2. 合并视频片段
                concat_file = self.create_concat_file(video_segments)
                temp_video = self.merge_segments(concat_file)
                
                # 3. 合并音频
                final_audio = self.merge_audio_tracks()
                
                # 4. 合成最终视频
                self.compose_final_video(temp_video, final_audio)
                
                self.signals.finished.emit(self.output_path)
                return
                
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    self.signals.error.emit(f"视频合成错误: {str(e)}")
                    return
                # continue to retry
            
    def check_ffmpeg(self):
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def default_output_path(self):
        import tempfile
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(tempfile.gettempdir(), f"novelvision_output_{timestamp}.mp4")
    
    def create_image_segment(self, image_path, duration=3.0, index=0):
        """将单张图片转换为视频片段"""
        seg_path = os.path.join(tempfile.gettempdir(), f"seg_{index}.mp4")
        
        cmd = [
            "ffmpeg", "-y",
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
    
    def merge_segments(self, concat_file):
        """合并视频片段"""
        merged = os.path.join(tempfile.gettempdir(), "merged.mp4")
        cmd = [
            "ffmpeg", "-y",
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
    
    def compose_final_video(self, video_input, audio_input):
        """合成最终视频"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_input,
            "-i", audio_input if audio_input else "anullsrc",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            self.output_path
        ]
        
        if not audio_input:
            cmd = [
                "ffmpeg", "-y",
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