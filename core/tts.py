#!/usr/bin/env python3
import sys
import os
import requests
import json
from PyQt5.QtCore import QThread, pyqtSignal
import tempfile
import base64
import time

class TTSWorker(QThread):
    signals = pyqtSignal(str, str)  # finished(audio_path), error(error_msg)
    
    def __init__(self, text, voice="zh-CN-XiaoxiaoNeural", max_retries=3):
        super().__init__()
        self.text = text
        self.voice = voice
        self.audio_path = None
        self.max_retries = max_retries
        
    def run(self):
        attempt = 0
        while attempt <= self.max_retries:
            try:
                if attempt > 0:
                    time.sleep(2 ** attempt)  # 指数退避: 2s, 4s
                    
                # 使用火山引擎 TTS API
                url = "https://api.volcengine.com/tts/v1/synthesize"
                
                api_key = self.get_api_key()
                if not api_key:
                    self.signals.error.emit("未配置火山引擎 API Key")
                    return
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                payload = {
                    "text": self.text,
                    "voice": self.voice,
                    "format": "mp3",
                    "speed": 1.0,
                    "pitch": 1.0
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code != 200:
                    error_text = response.text[:200] if response.text else "Unknown error"
                    attempt += 1
                    if attempt <= self.max_retries:
                        continue
                    else:
                        self.signals.error.emit(f"TTS API 失败 ({response.status_code}): {error_text}")
                        return
                
                result = response.json()
                if "audio" not in result:
                    attempt += 1
                    if attempt <= self.max_retries:
                        continue
                    else:
                        self.signals.error.emit(f"TTS 返回错误: {result}")
                        return
                    
                # 保存音频
                audio_data = result["audio"]
                self.audio_path = self.save_audio(audio_data)
                self.signals.finished.emit(self.audio_path)
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
                    self.signals.error.emit(f"TTS 错误: {str(e)}")
                    return
                # continue to retry
            
    def save_audio(self, audio_data):
        try:
            import base64
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tts_{timestamp}.mp3"
            filepath = os.path.join(tempfile.gettempdir(), filename)
            
            # 判断 audio_data 是 base64 字符串还是 URL
            if isinstance(audio_data, str) and audio_data.startswith("http"):
                # 下载 URL
                resp = requests.get(audio_data, timeout=30)
                if resp.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                else:
                    raise Exception(f"下载音频失败: {resp.status_code}")
            else:
                # base64 解码
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(audio_data))
                    
            return filepath
        except Exception as e:
            raise Exception(f"保存音频失败: {str(e)}")
    
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