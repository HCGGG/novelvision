#!/usr/bin/env python3
import sys
import os
import json
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import tempfile
from datetime import datetime
from core.image_gen import ImageGenWorker
from core.tts import TTSWorker
from core.video_composer import VideoComposerWorker

class WorkflowManager(QObject):
    progress_updated = pyqtSignal(int, str)  # percentage, message
    finished = pyqtSignal(str)  # output_path
    error_occurred = pyqtSignal(str)
    
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings
        self.project_data = {
            "name": "",
            "characters": [],
            "scenes": [],
            "config": {
                "resolution": "1920x1080",
                "fps": 30,
                "image_style": "anime",
                "voice": "zh-CN-XiaoxiaoNeural",
                "max_retries": 3
            }
        }
        self.is_running = False
        self.output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.workers = []
        self.output_path = None
        
        # 从 settings 覆盖默认配置
        if self.settings:
            self.project_data["config"]["resolution"] = self.settings.get("resolution", "1920x1080")
            self.project_data["config"]["fps"] = self.settings.get("fps", 30)
            self.project_data["config"]["voice"] = self.settings.get("voice", "zh-CN-XiaoxiaoNeural")
            self.project_data["config"]["max_retries"] = self.settings.get("max_retries", 3)
            self.output_dir = self.settings.get("output_dir", "output")
            os.makedirs(self.output_dir, exist_ok=True)
        
    def load_project(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.project_data = json.load(f)
            return True
        except Exception as e:
            self.error_occurred.emit(f"加载项目失败: {str(e)}")
            return False
    
    def save_project(self, filepath=None):
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.output_dir, f"project_{timestamp}.nvproj")
            
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.project_data, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            self.error_occurred.emit(f"保存项目失败: {str(e)}")
            return None
    
    def add_character(self, name, description, image_path=None):
        char = {
            "id": len(self.project_data["characters"]) + 1,
            "name": name,
            "description": description,
            "image": image_path,
            "voice": self.project_data["config"]["voice"]
        }
        self.project_data["characters"].append(char)
        return char
    
    def add_scene(self, description, characters=None, duration=5.0):
        scene = {
            "id": len(self.project_data["scenes"]) + 1,
            "description": description,
            "characters": characters or [],
            "duration": duration,
            "image": None,
            "audio": None
        }
        self.project_data["scenes"].append(scene)
        return scene
    
    def start(self):
        if self.is_running:
            return False
        self.is_running = True
        self.current_step = 0
        self.run_workflow_step()
        return True
    
    def stop(self):
        self.is_running = False
        for worker in self.workers:
            if worker.isRunning():
                worker.terminate()
    
    def run_workflow_step(self):
        """分步执行工作流，通过信号回调继续下一步"""
        try:
            if self.current_step == 0:
                self.progress_updated.emit(10, "生成场景图像...")
                self.generate_scene_images_async()
            elif self.current_step == 1:
                self.progress_updated.emit(40, "生成语音...")
                self.generate_audio_async()
            elif self.current_step == 2:
                self.progress_updated.emit(70, "合成视频...")
                self.compose_video_async()
            elif self.current_step == 3:
                self.progress_updated.emit(100, "完成")
                output_path = self.save_project()
                self.finished.emit(output_path)
                self.is_running = False
        except Exception as e:
            self.error_occurred.emit(f"工作流错误: {str(e)}")
            self.is_running = False
    
    def generate_scene_images_async(self):
        from core.image_gen import ImageGenWorker
        
        self.pending_image_gens = []
        for i, scene in enumerate(self.project_data["scenes"]):
            if not self.is_running:
                return
            if not scene["image"]:
                worker = ImageGenWorker(scene["description"], max_retries=self.project_data["config"]["max_retries"])
                worker.signals.finished.connect(self.on_image_generated)
                worker.signals.error.connect(self.on_error)
                self.workers.append(worker)
                self.pending_image_gens.append((scene, worker))
                worker.start()
        
        if not self.pending_image_gens:
            self.current_step += 1
            QTimer.singleShot(100, self.run_workflow_step)
    
    def on_image_generated(self, image_path):
        for scene, worker in self.pending_image_gens:
            if worker.sender() == worker:
                scene["image"] = image_path
                self.pending_image_gens.remove((scene, worker))
                break
        
        if not self.pending_image_gens:
            self.current_step += 1
            QTimer.singleShot(100, self.run_workflow_step)
    
    def generate_audio_async(self):
        from core.tts import TTSWorker
        
        self.pending_tts = []
        for i, scene in enumerate(self.project_data["scenes"]):
            if not self.is_running:
                return
            if not scene["audio"]:
                worker = TTSWorker(scene["description"], max_retries=self.project_data["config"]["max_retries"])
                worker.signals.finished.connect(self.on_audio_generated)
                worker.signals.error.connect(self.on_error)
                self.workers.append(worker)
                self.pending_tts.append((scene, worker))
                worker.start()
        
        if not self.pending_tts:
            self.current_step += 1
            QTimer.singleShot(100, self.run_workflow_step)
    
    def on_audio_generated(self, audio_path):
        for scene, worker in self.pending_tts:
            if worker.sender() == worker:
                scene["audio"] = audio_path
                self.pending_tts.remove((scene, worker))
                break
        
        if not self.pending_tts:
            self.current_step += 1
            QTimer.singleShot(100, self.run_workflow_step)
    
    def compose_video_async(self):
        from core.video_composer import VideoComposerWorker
        
        image_paths = [scene["image"] for scene in self.project_data["scenes"] if scene["image"]]
        audio_paths = [scene["audio"] for scene in self.project_data["scenes"] if scene["audio"]]
        
        if not image_paths:
            self.error_occurred.emit("没有可用的图像")
            self.is_running = False
            return
        
        worker = VideoComposerWorker(
            image_paths, 
            audio_paths,
            resolution=self.project_data["config"]["resolution"],
            fps=self.project_data["config"]["fps"],
            max_retries=self.project_data["config"]["max_retries"]
        )
        worker.signals.finished.connect(self.on_video_composed)
        worker.signals.error.connect(self.on_error)
        self.workers.append(worker)
        worker.start()
    
    def on_video_composed(self, video_path):
        self.output_path = video_path
        self.current_step += 1
        QTimer.singleShot(100, self.run_workflow_step)
    
    def on_error(self, error_msg):
        self.error_occurred.emit(error_msg)
        self.stop()