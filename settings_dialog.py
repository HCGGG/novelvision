#!/usr/bin/env python3
"""
NovelVision 设置对话框
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QPushButton, QLabel, QTabWidget, QWidget, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from settings import Settings

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 选项卡
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 常规选项卡
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("火山引擎 API Key")
        general_layout.addRow("API Key:", self.api_key_edit)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        output_btn = QPushButton("浏览...")
        output_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(output_btn)
        general_layout.addRow("输出目录:", output_layout)
        
        tabs.addTab(general_tab, "常规")
        
        # 视频选项卡
        video_tab = QWidget()
        video_layout = QFormLayout(video_tab)
        
        # 分辨率
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1920x1080", "1280x720", "854x480"])
        video_layout.addRow("分辨率:", self.resolution_combo)
        
        # FPS
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 120)
        self.fps_spin.setValue(30)
        video_layout.addRow("帧率 (FPS):", self.fps_spin)
        
        tabs.addTab(video_tab, "视频")
        
        # 语音选项卡
        voice_tab = QWidget()
        voice_layout = QFormLayout(voice_tab)
        
        # 语音角色
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
        voice_layout.addRow("语音角色:", self.voice_combo)
        
        tabs.addTab(voice_tab, "语音")
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        reset_btn = QPushButton("恢复默认")
        reset_btn.clicked.connect(self.reset_settings)
        btn_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_and_accept)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
    def load_settings(self):
        self.api_key_edit.setText(self.settings.get("volcengine_api_key", ""))
        self.output_dir_edit.setText(self.settings.get("output_dir", "output"))
        self.resolution_combo.setCurrentText(self.settings.get("resolution", "1920x1080"))
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
        self.settings.set("resolution", self.resolution_combo.currentText())
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