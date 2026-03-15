#!/usr/bin/env python3
import sys
import os
import requests
import json
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import tempfile
import base64
import time

class ImageGenWorker(QThread):
    signals = pyqtSignal(str, str)  # finished(image_path), error(error_msg)
    
    def __init__(self, description, max_retries=3):
        super().__init__()
        self.description = description
        self.image_path = None
        self.max_retries = max_retries
        
    def run(self):
        attempt = 0
        while attempt <= self.max_retries:
            try:
                if attempt > 0:
                    time.sleep(2 ** attempt)  # 指数退避: 2s, 4s
                    
                # 使用火山引擎图像生成 API
                url = "https://api.volcengine.com/image/v1/generate"
                
                api_key = self.get_api_key()
                if not api_key:
                    self.signals.error.emit("未配置火山引擎 API Key，请在配置文件中设置")
                    return
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                payload = {
                    "prompt": self.description,
                    "style": "anime",
                    "resolution": "1024x1024",
                    "num_images": 1
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code != 200:
                    error_text = response.text[:200] if response.text else "Unknown error"
                    attempt += 1
                    if attempt <= self.max_retries:
                        continue  # 重试
                    else:
                        self.signals.error.emit(f"API 请求失败 ({response.status_code}): {error_text}")
                        return
                
                result = response.json()
                
                if "images" not in result or not result["images"]:
                    attempt += 1
                    if attempt <= self.max_retries:
                        continue
                    else:
                        self.signals.error.emit(f"API 返回错误: {result}")
                        return
                
                # 保存图像
                image_data = result["images"][0]
                self.image_path = self.save_image(image_data)
                
                self.signals.finished.emit(self.image_path)
                return
                
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt > self.max_retries:
                    self.signals.error.emit(f"网络请求失败: {str(e)}")
                    return
                # continue to retry
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    self.signals.error.emit(f"图像生成错误: {str(e)}")
                    return
                # continue to retry
            
    def save_image(self, image_data):
        try:
            import base64
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"character_{timestamp}.png"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_data))
                
            return filepath
        except Exception as e:
            raise Exception(f"保存图像失败: {str(e)}")
    
    def get_api_key(self):
        try:
            import json
            import os
            
            config_path = os.path.expanduser("~/.openclaw/models.json")
            if not os.path.exists(config_path):
                return None
                
            with open(config_path, "r") as f:
                config = json.load(f)
                
            for model in config.get("models", []):
                if model.get("provider") == "volcengine":
                    return model.get("api_key")
                    
            return None
            
        except Exception:
            return None