#!/usr/bin/env python3
"""
NovelVision Pro - 小说人物视频生成器
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, QPushButton, QProgressBar, QLabel, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QSplitter, QScrollArea
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap

from core.workflow import WorkflowManager

class NovelVisionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovelVision Pro")
        self.setMinimumSize(1000, 700)
        
        # 初始化
        self.workflow = WorkflowManager()
        self.workflow.progress_updated.connect(self.update_progress)
        self.workflow.error_occurred.connect(self.show_error)
        self.workflow.finished.connect(self.on_workflow_finished)
        
        self.init_ui()
        self.check_dependencies()
    
    def init_ui(self):
        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        
        self.btn_new_project = QPushButton("🗄️ 新建项目")
        self.btn_new_project.clicked.connect(self.new_project)
        toolbar_layout.addWidget(self.btn_new_project)
        
        self.btn_save_project = QPushButton("💾 保存项目")
        self.btn_save_project.clicked.connect(self.save_project)
        toolbar_layout.addWidget(self.btn_save_project)
        
        self.btn_load_project = QPushButton("📂 加载项目")
        self.btn_load_project.clicked.connect(self.load_project)
        toolbar_layout.addWidget(self.btn_load_project)
        
        toolbar_layout.addStretch()
        
        self.btn_start = QPushButton("▶️ 开始生成")
        self.btn_start.clicked.connect(self.start_workflow)
        self.btn_start.setEnabled(False)
        toolbar_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⏹️ 停止")
        self.btn_stop.clicked.connect(self.stop_workflow)
        self.btn_stop.setEnabled(False)
        toolbar_layout.addWidget(self.btn_stop)
        
        layout.addWidget(toolbar)
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧面板（项目管理 + 角色编辑器）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 项目名称
        project_group = QWidget()
        project_layout = QVBoxLayout(project_group)
        project_layout.setContentsMargins(0, 0, 0, 0)
        
        project_label = QLabel("📄️ 项目名称:")
        project_layout.addWidget(project_label)
        
        self.project_name = QTextEdit()
        self.project_name.setMaximumHeight(30)
        self.project_name.setPlaceholderText("输入项目名称")
        project_layout.addWidget(self.project_name)
        
        left_layout.addWidget(project_group)
        
        # 角色列表
        char_group = QWidget()
        char_layout = QVBoxLayout(char_group)
        char_layout.setContentsMargins(0, 0, 0, 0)
        
        char_label = QLabel("👨️‍👩️‍👧️‍👦️ 角色设定:")
        char_layout.addWidget(char_label)
        
        self.char_list = QListWidget()
        self.char_list.itemClicked.connect(self.on_char_selected)
        char_layout.addWidget(self.char_list)
        
        self.btn_add_char = QPushButton("➕ 添加角色")
        self.btn_add_char.clicked.connect(self.add_character)
        char_layout.addWidget(self.btn_add_char)
        
        left_layout.addWidget(char_group)
        
        # 角色描述编辑器
        desc_group = QWidget()
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        
        desc_label = QLabel("📝 角色描述:")
        desc_layout.addWidget(desc_label)
        
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("描述角色外貌、服装、性格等细节")
        desc_layout.addWidget(self.char_desc)
        
        left_layout.addWidget(desc_group)
        
        splitter.addWidget(left_panel)
        
        # 右侧面板（工作流状态 + 输出）
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 工作流状态
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        status_label = QLabel("⚙️ 工作流状态:")
        status_layout.addWidget(status_label)
        
        self.workflow_status = QTextEdit()
        self.workflow_status.setMaximumHeight(80)
        self.workflow_status.setReadOnly(True)
        self.workflow_status.append("空闲")
        status_layout.addWidget(self.workflow_status)
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        status_layout.addWidget(self.progress)
        
        right_layout.addWidget(status_group)
        
        # 场景列表
        scene_group = QWidget()
        scene_layout = QVBoxLayout(scene_group)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        
        scene_label = QLabel("🎭 场景/分镜:")
        scene_layout.addWidget(scene_label)
        
        self.scene_list = QListWidget()
        scene_layout.addWidget(self.scene_list)
        
        self.btn_add_scene = QPushButton("➕ 添加场景")
        self.btn_add_scene.clicked.connect(self.add_scene)
        scene_layout.addWidget(self.btn_add_scene)
        
        right_layout.addWidget(scene_group)
        
        # 预览区域
        preview_group = QWidget()
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_label = QLabel("🖼️ 预览:")
        preview_layout.addWidget(preview_label)
        
        self.preview_label = QLabel("暂无预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(True)
        self.preview_label.setMinimumSize(300, 200)
        preview_layout.addWidget(self.preview_label)
        
        right_layout.addWidget(preview_group)
        
        # 日志区域
        log_group = QWidget()
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(0, 0, 0, 0)
        
        log_label = QLabel("📝 日志:")
        log_layout.addWidget(log_label)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        log_layout.addWidget(self.log_area)
        
        right_layout.addWidget(log_group)
        
        splitter.addWidget(right_panel)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("NovelVision Pro - 小说人物视频生成器")
    
    def check_dependencies(self):
        """检查依赖并显示状态"""
        # 检查 FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            self.status_bar.showMessage("FFmpeg: ✓ 可用", 2000)
        except:
            self.status_bar.showMessage("FFmpeg: ✗ 未找到，请安装", 5000)
    
    def new_project(self):
        self.project_name.clear()
        self.char_list.clear()
        self.char_desc.clear()
        self.scene_list.clear()
        self.preview_label.setText("暂无预览")
        self.workflow.project_data = {
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
        self.btn_start.setEnabled(True)
        self.log_area.append("📄️ 新建项目")
    
    def save_project(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "保存项目", "", "NovelVision 项目 (*.nvproj)")
        if filepath:
            self.workflow.project_data["name"] = self.project_name.toPlainText()
            saved_path = self.workflow.save_project(filepath)
            if saved_path:
                self.log_area.append(f"💾 项目保存成功: {saved_path}")
            else:
                self.log_area.append("❌ 项目保存失败")
    
    def load_project(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "加载项目", "", "NovelVision 项目 (*.nvproj)")
        if filepath:
            if self.workflow.load_project(filepath):
                self.project_name.setPlainText(self.workflow.project_data.get("name", ""))
                self.char_list.clear()
                for char in self.workflow.project_data.get("characters", []):
                    item = QListWidgetItem(f"👨️ {char['name']}")
                    self.char_list.addItem(item)
                self.scene_list.clear()
                for scene in self.workflow.project_data.get("scenes", []):
                    item = QListWidgetItem(f"🎭 {scene['description']}")
                    self.scene_list.addItem(item)
                self.log_area.append(f"📂 项目加载成功: {filepath}")
                self.btn_start.setEnabled(True)
            else:
                self.log_area.append("❌ 项目加载失败")
    
    def add_character(self):
        char_name = f"角色{len(self.workflow.project_data['characters']) + 1}"
        char_desc = "描述角色外貌、服装、性格等细节"
        char = self.workflow.add_character(char_name, char_desc)
        
        item = QListWidgetItem(f"👨️ {char_name}")
        self.char_list.addItem(item)
        self.char_list.setCurrentItem(item)
        
        self.char_desc.setPlainText(char_desc)
        self.log_area.append(f"➕ 添加角色: {char_name}")
    
    def on_char_selected(self, item):
        char_id = self.char_list.row(item)
        if char_id < len(self.workflow.project_data['characters']):
            char = self.workflow.project_data['characters'][char_id]
            self.char_desc.setPlainText(char['description'])
    
    def add_scene(self):
        scene_desc = f"场景{len(self.workflow.project_data['scenes']) + 1}"
        scene = self.workflow.add_scene(scene_desc)
        
        item = QListWidgetItem(f"🎭 {scene_desc}")
        self.scene_list.addItem(item)
        self.scene_list.setCurrentItem(item)
        
        self.log_area.append(f"➕ 添加场景: {scene_desc}")
    
    def start_workflow(self):
        self.workflow.project_data["name"] = self.project_name.toPlainText()
        self.workflow.project_data["characters"] = []
        
        # 从界面获取角色信息
        for i in range(self.char_list.count()):
            item = self.char_list.item(i)
            char_desc = self.char_desc.toPlainText()
            char = {
                "id": i + 1,
                "name": item.text().replace("👨️ ", ""),
                "description": char_desc,
                "image": None,
                "voice": self.workflow.project_data["config"]["voice"]
            }
            self.workflow.project_data["characters"].append(char)
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.log_area.append("▶️ 开始工作流...")
        
        if self.workflow.start():
            self.workflow_status.append("工作流: 运行中")
        else:
            self.workflow_status.append("工作流: 启动失败")
            self.btn_start.setEnabled(True)
    
    def stop_workflow(self):
        self.workflow.stop()
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        self.workflow_status.append("工作流: 已停止")
        self.log_area.append("⏹️ 工作流已停止")
    
    def update_progress(self, percentage, message):
        self.progress.setValue(percentage)
        self.workflow_status.append(f"⚙️ {message}")
        self.log_area.append(f"⚙️ {message}")
    
    def show_error(self, error_msg):
        self.workflow_status.append(f"❌ {error_msg}")
        self.log_area.append(f"❌ {error_msg}")
        QMessageBox.critical(self, "错误", error_msg)
    
    def on_workflow_finished(self, output_path):
        self.btn_stop.setEnabled(False)
        self.btn_start.setEnabled(True)
        self.workflow_status.append(f"✅ 工作流完成")
        self.log_area.append(f"✅ 工作流完成: {output_path}")
        
        # 显示预览
        if os.path.exists(output_path):
            self.preview_label.setText(f"🖼️ 预览: {output_path}")
        else:
            self.preview_label.setText("🖼️ 预览: 无")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置样式
    app.setStyle('Fusion')
    
    window = NovelVisionGUI()
    window.show()
    
    sys.exit(app.exec_())