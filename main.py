#!/usr/bin/env python3
"""
NovelVision Pro - 小说人物视频生成器
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication

# 导入优化后的 GUI 类和关于对话框
from gui import NovelVisionGUI, AboutDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = NovelVisionGUI()
    window.show()
    
    sys.exit(app.exec_())
