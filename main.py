#!/usr/bin/env python3
"""
NovelVision GUI - PyQt5 界面（优化版）
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QPushButton, QProgressBar, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QStatusBar, QAction,
    QToolBar, QApplication, QDialog, QFormLayout, QLineEdit, QTextEdit as QTextEditWidget,
    QGroupBox, QFrame, QSizePolicy, QMediaPlayer, QVideoWidget
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
import os
import time

from core.workflow import WorkflowManager
from settings import Settings
from settings_dialog import SettingsDialog

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 NovelVision Pro")
        self.setMinimumWidth(420)
        self.setMaximumWidth(420)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # 标题
        title = QLabel("NovelVision Pro")
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #2c3e50;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(line)
        
        # 版本信息
        version_info = QLabel("版本: 0.1.0")
        version_info.setStyleSheet("""
            font-size: 14px; 
            color: #555;
        """)
        version_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_info)
        
        try:
            import version
            version_info.setText(f"版本: 0.1.0 (build: {version.BUILD_RUN_NUMBER}, commit: {version.BUILD_COMMIT_SHA[:7]})")
        except:
            pass
        
        # 描述
        desc = QLabel("小说人物视频生成器")
        desc.setStyleSheet("""
            font-size: 13px; 
            color: #666;
        """)
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # 技术栈
        tech_stack = QLabel("技术栈: PyQt5 + 火山引擎 AI + FFmpeg（内置）")
        tech_stack.setStyleSheet("""
            font-size: 11px; 
            color: #888;
        """)
        tech_stack.setAlignment(Qt.AlignCenter)
        layout.addWidget(tech_stack)
        
        layout.addStretch()
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.setMinimumWidth(100)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 版权信息
        license_info = QLabel("\u00a9 2026 NovelVision Pro")
        license_info.setStyleSheet("""
            font-size: 10px; 
            color: #aaa;
        """)
        license_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_info)

class NovelVisionGUI(QMainWindow):
    """主GUI窗口，包含场景管理、AI生成过程显示和交互逻辑。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.workflow = WorkflowManager(settings=self.settings)
        self.project_data = {
            "name": "",
            "characters": [],
            "scenes": [],
            "config": {
                "resolution": "1920x1080",
                "fps": 30,
                "image_style": "anime",
                "voice": "zh-CN-XiaoxiaoNeural"
            }
        }
        self.workflow.project_data = self.project_data
        self.current_scene_index = -1
        self.preview_worker = None
        self.media_player = None
        self.video_widget = None
        
        # 设置窗口属性
        self.setWindowTitle("NovelVision Pro")
        self.setMinimumSize(1600, 1000)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        # 创建主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
            }
            QSplitter::handle:hover {
                background-color: #bdc3c7;
            }
        """)
        
        # 左侧面板
        left_panel = QWidget()
        left_panel.setMaximumWidth(450)
        left_panel.setStyleSheet("background-color: #ffffff;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(16)
        left_layout.setContentsMargins(12, 12, 12, 12)
        
        # 项目名称
        project_group = QGroupBox("\ud83d\udcc4 \u9879\u76ee")
        project_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        project_layout = QVBoxLayout(project_group)
        project_layout.setSpacing(8)
        project_layout.setContentsMargins(12, 12, 12, 12)
        
        self.project_name = QTextEdit("\u6211\u7684\u5c0f\u8bf4\u89c6\u9891")
        self.project_name.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                min-height: 32px;
            }
        """)
        project_layout.addWidget(self.project_name)
        left_layout.addWidget(project_group)
        
        # 角色管理
        char_group = QGroupBox("\ud83d\udc64 \u89d2\u8272")
        char_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        char_layout = QVBoxLayout(char_group)
        char_layout.setSpacing(8)
        char_layout.setContentsMargins(12, 12, 12, 12)
        
        self.char_list = QListWidget()
        self.char_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #ecf0f1;
            }
        """)
        self.char_list.itemClicked.connect(self.on_char_selected)
        char_layout.addWidget(self.char_list)
        
        # 角色按钮
        char_btn_layout = QHBoxLayout()
        char_btn_layout.setSpacing(6)
        
        self.btn_add_char = QPushButton("\u2795 \u6dfb\u52a0")
        self.btn_add_char.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_add_char.clicked.connect(self.add_character)
        char_btn_layout.addWidget(self.btn_add_char)
        
        self.btn_del_char = QPushButton("\ud83d\uddd1\ufe0f \u5220\u9664")
        self.btn_del_char.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.btn_del_char.clicked.connect(self.delete_character)
        char_btn_layout.addWidget(self.btn_del_char)
        char_layout.addLayout(char_btn_layout)
        
        left_layout.addWidget(char_group)
        
        # 角色描述
        desc_group = QGroupBox("\ud83d\udcdd \u89d2\u8272\u63cf\u8ff0")
        desc_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setSpacing(8)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("\u63cf\u8ff0\u89d2\u8272\u5916\u8c8c\u3001\u670d\u88c5\u3001\u6027\u683c\u7b49\u7ec6\u8282...")
        self.char_desc.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                min-height: 80px;
            }
        """)
        desc_layout.addWidget(self.char_desc)
        left_layout.addWidget(desc_group)
        
        left_layout.addStretch()
        
        # 右侧面板
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #ffffff;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)
        right_layout.setContentsMargins(12, 12, 12, 12)
        
        # 剧情输入
        plot_group = QGroupBox("\ud83d\udd8b\ufe0f \u5267\u60c5")
        plot_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        plot_layout = QVBoxLayout(plot_group)
        plot_layout.setSpacing(8)
        plot_layout.setContentsMargins(12, 12, 12, 12)
        
        self.plot_text = QTextEdit()
        self.plot_text.setPlaceholderText("\u8f93\u5165\u5267\u60c5\uff0c\u6bcf\u4e2a\u573a\u666f\u7528\u7a7a\u884c\u5206\u9694\uff0c\u5982\uff1a\n\n\u7b2c\u4e00\u5c40\uff1a\n\n\u4e3b\u89d2\u8d70\u5728\u6821\u56ed\u91cc\uff0c\n\n\u770b\u5230\u8fdc\u5904\u4e00\u4f4d\u5973\u751f\u5728\u8bfb\u4e66\u3002\n\n\n\u7b2c\u4e8c\u5c40\uff1a\n\n\u4e24\u4eba\u76f8\u9047\uff0c\n\n\u5f00\u59cb\u4ea4\u4e92\u3002")
        self.plot_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                min-height: 120px;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        self.plot_text.textChanged.connect(self.check_plot_ready)
        plot_layout.addWidget(self.plot_text)
        
        # 剧情按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.btn_confirm_plot = QPushButton("\u786e\u8ba4\u5267\u60c5")
        self.btn_confirm_plot.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.btn_confirm_plot.clicked.connect(self.confirm_plot)
        btn_layout.addWidget(self.btn_confirm_plot)
        
        plot_layout.addLayout(btn_layout)
        
        right_layout.addWidget(plot_group)

        # --- 预览 & 日志 ---
        bottom_splitter = QSplitter(Qt.Vertical)
        bottom_splitter.setHandleWidth(6)
        bottom_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
            }
            QSplitter::handle:hover {
                background-color: #bdc3c7;
            }
        """)
        
        # 预览区域
        preview_group = QGroupBox("\ud83d\uddbc\ufe0f \u9884\u89c8")
        preview_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                sub