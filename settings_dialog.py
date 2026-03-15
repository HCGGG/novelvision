#!/usr/bin/env python3
"""
NovelVision 设置对话框（优化版）
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QLabel, QTabWidget, QWidget, QMessageBox, QFileDialog,
    QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle("设置 - NovelVision Pro")
        self.setMinimumWidth(520)
        self.setMaximumWidth(520)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 选项卡
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #555;
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #d0d0d0;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e8e8e8;
            }
        """)
        layout.addWidget(tabs)
        
        # ==================== 常规选项卡 ====================
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setSpacing(12)
        general_layout.setContentsMargins(16, 16, 16, 16)
        
        # API 设置组
        api_group = QGroupBox("API 配置")
        api_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
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
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(10)
        api_layout.setContentsMargins(12, 16, 12, 12)
        api_layout.setLabelAlignment(Qt.AlignRight)
        
        api_label = QLabel("API Key:")
        api_label.setStyleSheet("color: #555; font-size: 12px;")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("请输入火山引擎 API Key")
        self.api_key_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        api_layout.addRow(api_label, self.api_key_edit)
        
        general_layout.addWidget(api_group)
        
        # 输出目录组
        output_group = QGroupBox("输出设置")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
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
        output_layout = QFormLayout(output_group)
        output_layout.setSpacing(10)
        output_layout.setContentsMargins(12, 16, 12, 12)
        output_layout.setLabelAlignment(Qt.AlignRight)
        
        output_label = QLabel("输出目录:")
        output_label.setStyleSheet("color: #555; font-size: 12px;")
        output_hbox = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: #f8f9fa;
                font-size: 12px;
            }
        """)
        output_btn = QPushButton("浏览...")
        output_btn.setMinimumWidth(80)
        output_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        output_btn.clicked.connect(self.browse_output_dir)
        output_hbox.addWidget(self.output_dir_edit)
        output_hbox.addWidget(output_btn)
        output_layout.addRow(output_label, output_hbox)
        
        general_layout.addWidget(output_group)
        general_layout.addStretch()
        
        tabs.addTab(general_tab, "常规")
        
        # ==================== 视频选项卡 ====================
        video_tab = QWidget()
        video_layout = QVBoxLayout(video_tab)
        video_layout.setSpacing(12)
        video_layout.setContentsMargins(16, 16, 16, 16)
        
        video_group = QGroupBox("视频参数")
        video_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
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
        video_form_layout = QFormLayout(video_group)
        video_form_layout.setSpacing(10)
        video_form_layout.setContentsMargins(12, 16, 12, 12)
        video_form_layout.setLabelAlignment(Qt.AlignRight)
        
        # 分辨率
        res_label = QLabel("分辨率:")
        res_label.setStyleSheet("color: #555; font-size: 12px;")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1920x1080 (1080p)", "1280x720 (720p)", "854x480 (480p)"])
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 12px;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)
        video_form_layout.addRow(res_label, self.resolution_combo)
        
        # FPS
        fps_label = QLabel("帧率 (FPS):")
        fps_label.setStyleSheet("color: #555; font-size: 12px;")
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(30)
        self.fps_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 12px;
                min-width: 100px;
            }
            QSpinBox:focus {
                border: 1px solid #3498db;
            }
        """)
        video_form_layout.addRow(fps_label, self.fps_spin)
        
        video_layout.addWidget(video_group)
        video_layout.addStretch()
        
        tabs.addTab(video_tab, "视频")
        
        # ==================== 语音选项卡 ====================
        voice_tab = QWidget()
        voice_layout = QVBoxLayout(voice_tab)
        voice_layout.setSpacing(12)
        voice_layout.setContentsMargins(16, 16, 16, 16)
        
        voice_group = QGroupBox("语音设置")
        voice_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
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
        voice_form_layout = QFormLayout(voice_group)
        voice_form_layout.setSpacing(10)
        voice_form_layout.setContentsMargins(12, 16, 12, 12)
        voice_form_layout.setLabelAlignment(Qt.AlignRight)
        
        # 语音角色
        voice_label = QLabel("语音角色:")
        voice_label.setStyleSheet("color: #555; font-size: 12px;")
        self.voice_combo = QComboBox()
        voices = [
            ("zh-CN-XiaoxiaoNeural", "晓晓 - 女声 (默认)"),
            ("zh-CN-YunxiNeural", "云希 - 男声"),
            ("zh-CN-YunjianNeural", "云健 - 男声"),
            ("zh-CN-XiaoyiNeural", "晓伊 - 女声"),
            ("zh-CN-XiaomoNeural", "晓墨 - 女声"),
        ]
        for value, label in voices:
            self.voice_combo.addItem(label, value)
        self.voice_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 12px;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)
        voice_form_layout.addRow(voice_label, self.voice_combo)
        
        voice_layout.addWidget(voice_group)
        voice_layout.addStretch()
        
        tabs.addTab(voice_tab, "语音")
        
        # ==================== 底部按钮 ====================
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        reset_btn = QPushButton("恢复默认")
        reset_btn.setMinimumWidth(100)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #a04000;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        btn_layout.addWidget(reset_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setMinimumWidth(100)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        save_btn.clicked.connect(self.save_and_accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
    def load_settings(self):
        self.api_key_edit.setText(self.settings.get("volcengine_api_key", ""))
        self.output_dir_edit.setText(self.settings.get("output_dir", "output"))
        
        # 处理分辨率显示（去掉后缀）
        res = self.settings.get("resolution", "1920x1080")
        res_map = {
            "1920x1080": "1920x1080 (1080p)",
            "1280x720": "1280x720 (720p)",
            "854x480": "854x480 (480p)"
        }
        self.resolution_combo.setCurrentText(res_map.get(res, "1920x1080 (1080p)"))
        
        self.fps_spin.setValue(self.settings.get("fps", 30))
        voice = self.settings.get("voice", "zh-CN-XiaoxiaoNeural")
        idx = self.voice_combo.findData(voice)
        if idx >= 0:
            self.voice_combo.setCurrentIndex(idx)
    
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录", self.output_dir_edit.text())
        if directory:
            self.output_dir_edit.setText(directory)
    
    def save_and_accept(self):
        # 收集数据
        self.settings.set("volcengine_api_key", self.api_key_edit.text().strip())
        self.settings.set("output_dir", self.output_dir_edit.text().strip())
        
        # 处理分辨率（提取纯数值）
        res_text = self.resolution_combo.currentText()
        res = res_text.split(" ")[0]
        self.settings.set("resolution", res)
        
        self.settings.set("fps", self.fps_spin.value())
        self.settings.set("voice", self.voice_combo.currentData())
        
        # 保存
        if self.settings.save():
            QMessageBox.information(self, "保存成功", "设置已保存。")
            self.accept()
        else:
            QMessageBox.warning(self, "保存失败", "无法保存配置文件，请检查权限。")
    
    def reset_settings(self):
        reply = QMessageBox.question(
            self, "恢复默认",
            "确定要恢复所有设置为默认值吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.settings.reset()
            self.load_settings()
            QMessageBox.information(self, "已恢复", "设置已恢复为默认值。")
