#!/usr/bin/env python3
"""
NovelVision GUI - PyQt5 界面
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QPushButton, QProgressBar, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QStatusBar, QAction,
    QToolBar, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
import os

from core.workflow import WorkflowManager
from settings import Settings
from settings_dialog import SettingsDialog

class NovelVisionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.workflow = WorkflowManager(settings=self.settings)
        
        self.setWindowTitle("NovelVision Pro")
        self.setMinimumSize(1100, 750)
        
        self.init_ui()
        self.connect_signals()
        self.check_dependencies()
        self.update_status_bar()
    
    def init_ui(self):
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 工具栏
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        self.action_new = QAction("🗄️ 新建", self)
        self.action_new.triggered.connect(self.new_project)
        toolbar.addAction(self.action_new)
        
        self.action_save = QAction("💾 保存", self)
        self.action_save.triggered.connect(self.save_project)
        toolbar.addAction(self.action_save)
        
        self.action_load = QAction("📂 加载", self)
        self.action_load.triggered.connect(self.load_project)
        toolbar.addAction(self.action_load)
        
        toolbar.addSeparator()
        
        self.action_settings = QAction("⚙️ 设置", self)
        self.action_settings.triggered.connect(self.open_settings)
        toolbar.addAction(self.action_settings)
        
        toolbar.addSeparator()
        
        self.action_start = QAction("▶️ 开始生成", self)
        self.action_start.triggered.connect(self.start_workflow)
        self.action_start.setEnabled(False)
        toolbar.addAction(self.action_start)
        
        self.action_stop = QAction("⏹️ 停止", self)
        self.action_stop.triggered.connect(self.stop_workflow)
        self.action_stop.setEnabled(False)
        toolbar.addAction(self.action_stop)
        
        # 主分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        
        # 项目名称
        project_group = QWidget()
        project_layout = QVBoxLayout(project_group)
        project_layout.setContentsMargins(0, 0, 0, 0)
        project_label = QLabel("📄 项目名称:")
        project_label.setStyleSheet("font-weight: bold;")
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
        char_label = QLabel("👥 角色设定:")
        char_label.setStyleSheet("font-weight: bold;")
        char_layout.addWidget(char_label)
        
        self.char_list = QListWidget()
        self.char_list.itemClicked.connect(self.on_char_selected)
        char_layout.addWidget(self.char_list)
        
        btn_layout = QHBoxLayout()
        self.btn_add_char = QPushButton("➕ 添加角色")
        self.btn_add_char.clicked.connect(self.add_character)
        btn_layout.addWidget(self.btn_add_char)
        self.btn_del_char = QPushButton("🗑️ 删除角色")
        self.btn_del_char.clicked.connect(self.delete_character)
        btn_layout.addWidget(self.btn_del_char)
        char_layout.addLayout(btn_layout)
        
        left_layout.addWidget(char_group)
        
        # 角色描述
        desc_group = QWidget()
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_label = QLabel("📝 角色描述:")
        desc_label.setStyleSheet("font-weight: bold;")
        desc_layout.addWidget(desc_label)
        
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("描述角色外貌、服装、性格等细节")
        desc_layout.addWidget(self.char_desc)
        
        left_layout.addWidget(desc_group)
        
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        
        # 工作流状态
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_label = QLabel("⚙️ 工作流状态:")
        status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(status_label)
        
        self.workflow_status = QTextEdit()
        self.workflow_status.setMaximumHeight(100)
        self.workflow_status.setReadOnly(True)
        self.workflow_status.setStyleSheet("background-color: #f0f0f0; font-family: monospace;")
        self.workflow_status.append("就绪")
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
        scene_label.setStyleSheet("font-weight: bold;")
        scene_layout.addWidget(scene_label)
        
        self.scene_list = QListWidget()
        scene_layout.addWidget(self.scene_list)
        
        btn_layout2 = QHBoxLayout()
        self.btn_add_scene = QPushButton("➕ 添加场景")
        self.btn_add_scene.clicked.connect(self.add_scene)
        btn_layout2.addWidget(self.btn_add_scene)
        self.btn_del_scene = QPushButton("🗑️ 删除场景")
        self.btn_del_scene.clicked.connect(self.delete_scene)
        btn_layout2.addWidget(self.btn_del_scene)
        scene_layout.addLayout(btn_layout2)
        
        right_layout.addWidget(scene_group)
        
        # 预览区域
        preview_group = QWidget()
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_label = QLabel("🖼️ 预览:")
        preview_label.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_label)
        
        self.preview_label = QLabel("暂无预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #fafafa;")
        self.preview_label.setMinimumSize(320, 180)
        self.preview_label.setScaledContents(True)
        preview_layout.addWidget(self.preview_label)
        
        right_layout.addWidget(preview_group)
        
        # 日志区域
        log_group = QWidget()
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_label = QLabel("📝 日志:")
        log_label.setStyleSheet("font-weight: bold;")
        log_layout.addWidget(log_label)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setStyleSheet("background-color: #f8f8f8; font-family: Consolas, monospace;")
        log_layout.addWidget(self.log_area)
        
        right_layout.addWidget(log_group)
        
        splitter.addWidget(right_panel)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("NovelVision Pro - 小说人物视频生成器")
    
    def connect_signals(self):
        self.workflow.progress_updated.connect(self.update_progress)
        self.workflow.error_occurred.connect(self.show_error)
        self.workflow.finished.connect(self.on_workflow_finished)
    
    def check_dependencies(self):
        try:
            import ffmpeg
            self.status_bar.showMessage("FFmpeg: ✓ 可用", 3000)
        except ImportError:
            self.status_bar.showMessage("警告: FFmpeg 未安装，视频合成将失败", 5000)
    
    def update_status_bar(self):
        config = self.workflow.project_data["config"]
        text = f"分辨率: {config['resolution']} | FPS: {config['fps']} | 语音: {config['voice']}"
        self.status_bar.addPermanentWidget(QLabel(text))
    
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
            "config": self.workflow.project_data["config"].copy()
        }
        self.action_start.setEnabled(True)
        self.log_area.append("📄 新建项目")
    
    def save_project(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "保存项目", self.settings.get("output_dir", "output"),
            "NovelVision 项目 (*.nvproj)"
        )
        if filepath:
            self.workflow.project_data["name"] = self.project_name.toPlainText()
            # 同步角色描述
            self.sync_characters_from_ui()
            saved_path = self.workflow.save_project(filepath)
            if saved_path:
                self.log_area.append(f"💾 项目保存成功: {saved_path}")
            else:
                self.log_area.append("❌ 项目保存失败")
    
    def load_project(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "加载项目", self.settings.get("output_dir", "output"),
            "NovelVision 项目 (*.nvproj)"
        )
        if filepath:
            if self.workflow.load_project(filepath):
                self.project_name.setPlainText(self.workflow.project_data.get("name", ""))
                self.char_list.clear()
                for char in self.workflow.project_data.get("characters", []):
                    item = QListWidgetItem(f"👤 {char['name']}")
                    self.char_list.addItem(item)
                self.scene_list.clear()
                for scene in self.workflow.project_data.get("scenes", []):
                    item = QListWidgetItem(f"🎬 {scene['description']}")
                    self.scene_list.addItem(item)
                self.log_area.append(f"📂 项目加载成功: {filepath}")
                self.action_start.setEnabled(True)
            else:
                self.log_area.append("❌ 项目加载失败")
    
    def sync_characters_from_ui(self):
        # 将 UI 中的角色描述同步到 project_data
        chars = []
        for i in range(self.char_list.count()):
            item = self.char_list.item(i)
            name = item.text().replace("👤 ", "")
            desc = self.char_desc.toPlainText() if i == self.char_list.currentRow() else ""
            char = {
                "id": i + 1,
                "name": name,
                "description": desc,
                "image": None,
                "voice": self.workflow.project_data["config"]["voice"]
            }
            chars.append(char)
        self.workflow.project_data["characters"] = chars
    
    def add_character(self):
        char_name = f"角色{len(self.workflow.project_data['characters']) + 1}"
        char_desc = ""
        char = self.workflow.add_character(char_name, char_desc)
        
        item = QListWidgetItem(f"👤 {char_name}")
        self.char_list.addItem(item)
        self.char_list.setCurrentItem(item)
        self.char_desc.setPlainText(char_desc)
        
        self.log_area.append(f"➕ 添加角色: {char_name}")
    
    def delete_character(self):
        row = self.char_list.currentRow()
        if row >= 0:
            name = self.char_list.item(row).text().replace("👤 ", "")
            self.char_list.takeItem(row)
            self.char_desc.clear()
            self.workflow.project_data["characters"].pop(row)
            self.log_area.append(f"🗑️ 删除角色: {name}")
    
    def on_char_selected(self, item):
        char_id = self.char_list.row(item)
        if char_id < len(self.workflow.project_data['characters']):
            char = self.workflow.project_data['characters'][char_id]
            self.char_desc.setPlainText(char['description'])
    
    def add_scene(self):
        scene_desc = f"场景{len(self.workflow.project_data['scenes']) + 1}"
        scene = self.workflow.add_scene(scene_desc)
        
        item = QListWidgetItem(f"🎬 {scene_desc}")
        self.scene_list.addItem(item)
        self.scene_list.setCurrentItem(item)
        
        self.log_area.append(f"➕ 添加场景: {scene_desc}")
    
    def delete_scene(self):
        row = self.scene_list.currentRow()
        if row >= 0:
            desc = self.scene_list.item(row).text().replace("🎬 ", "")
            self.scene_list.takeItem(row)
            self.workflow.project_data["scenes"].pop(row)
            self.log_area.append(f"🗑️ 删除场景: {desc}")
    
    def start_workflow(self):
        self.sync_characters_from_ui()
        self.workflow.project_data["name"] = self.project_name.toPlainText()
        
        if not self.workflow.project_data["scenes"]:
            QMessageBox.warning(self, "警告", "请至少添加一个场景。")
            return
        
        self.action_start.setEnabled(False)
        self.action_stop.setEnabled(True)
        self.log_area.append("▶️ 开始工作流...")
        
        if self.workflow.start():
            self.workflow_status.append("工作流: 运行中")
        else:
            self.workflow_status.append("工作流: 启动失败")
            self.action_start.setEnabled(True)
    
    def stop_workflow(self):
        self.workflow.stop()
        self.action_stop.setEnabled(False)
        self.action_start.setEnabled(True)
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
        self.action_stop.setEnabled(False)
        self.action_start.setEnabled(True)
        self.workflow_status.append(f"✅ 工作流完成")
        self.log_area.append(f"✅ 工作流完成: {output_path}")
        self.preview_label.setText(f"✅ 视频已生成\n{output_path}")
    
    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self.update_status_bar()
            self.log_area.append("⚙️ 设置已更新")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    window = NovelVisionGUI()
    window.show()
    sys.exit(app.exec_())