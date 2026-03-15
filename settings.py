#!/usr/bin/env python3
"""
NovelVision 设置管理
"""

import os
import json
from pathlib import Path

class Settings:
    def __init__(self, config_path=None):
        self.config_path = config_path or self.default_config_path()
        self.defaults = {
            "volcengine_api_key": "",
            "resolution": "1920x1080",
            "fps": 30,
            "voice": "zh-CN-XiaoxiaoNeural",
            "image_style": "anime",
            "max_retries": 3,
            "output_dir": "output"
        }
        self.data = self.load()
        
    def default_config_path(self):
        # 优先使用当前目录的 config.json
        local = Path("config.json")
        if local.exists():
            return str(local)
        # 其次使用用户目录
        user_dir = Path.home() / ".novelvision"
        user_dir.mkdir(exist_ok=True)
        return str(user_dir / "config.json")
    
    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 合并默认值
                for k, v in self.defaults.items():
                    if k not in data:
                        data[k] = v
                return data
            except Exception:
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
        
    def reset(self):
        self.data = self.defaults.copy()
        self.save()