#!/usr/bin/env python3
"""
NovelVision GUI - PyQt5 界面（优化版）
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QPushButton, QProgressBar, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QStatusBar, QAction,
    QToolBar, QApplication, QDialog, QFormLayout, QLineEdit, QTextEdit as QTextEditWidget,
    QGroupBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
import os

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
        license_info = QLabel("© 2026 NovelVision Pro")
        license_info.setStyleSheet("""
            font-size: 10px; 
            color: #aaa;
        """)
        license_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(license_info)


class NovelVisionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.workflow = WorkflowManager(settings=self.settings)
        
        self.setWindowTitle("NovelVision Pro")
        self.setMinimumSize(1400, 900)
        
        self.init_ui()
        self.connect_signals()
        self.check_dependencies()
        self.update_status_bar()
        self.update_window_title()
    
    def init_ui(self):
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # 工具栏
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
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
        
        self.action_about = QAction("ℹ️ 关于", self)
        self.action_about.triggered.connect(self.open_about)
        toolbar.addAction(self.action_about)
        
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
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
            }
            QSplitter::handle:hover {
                background-color: #bdc3c7;
            }
        """)
        main_layout.addWidget(splitter)
        
        # ==================== 左侧面板 ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- 项目信息 ---
        project_group = QGroupBox("📄 项目信息")
        project_group.setStyleSheet("""
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
        project_layout = QVBoxLayout(project_group)
        project_layout.setSpacing(8)
        project_layout.setContentsMargins(12, 12, 12, 12)
        
        project_label = QLabel("项目名称:")
        project_label.setStyleSheet("color: #555; font-size: 12px;")
        project_layout.addWidget(project_label)
        
        self.project_name = QTextEdit()
        self.project_name.setMaximumHeight(32)
        self.project_name.setPlaceholderText("输入项目名称...")
        self.project_name.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        project_layout.addWidget(self.project_name)
        
        left_layout.addWidget(project_group)
        
        # --- 角色设定 ---
        char_group = QGroupBox("👥 角色设定")
        char_group.setStyleSheet("""
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
        char_layout = QVBoxLayout(char_group)
        char_layout.setSpacing(8)
        char_layout.setContentsMargins(12, 12, 12, 12)
        
        self.char_list = QListWidget()
        self.char_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
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
        
        self.btn_add_char = QPushButton("➕ 添加")
        self.btn_add_char.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
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
        
        self.btn_del_char = QPushButton("🗑️ 删除")
        self.btn_del_char.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
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
        
        # --- 角色描述 ---
        desc_group = QGroupBox("📝 角色描述")
        desc_group.setStyleSheet("""
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
        desc_layout = QVBoxLayout(desc_group)
        desc_layout.setSpacing(8)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("描述角色外貌、服装、性格等细节...")
        self.char_desc.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        desc_layout.addWidget(self.char_desc)
        
        left_layout.addWidget(desc_group)
        
        splitter.addWidget(left_panel)
        
        # ==================== 右侧面板 ====================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- 工作流状态 ---
        status_group = QGroupBox("⚙️ 工作流状态")
        status_group.setStyleSheet("""
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
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(8)
        status_layout.setContentsMargins(12, 12, 12, 12)
        
        self.workflow_status = QTextEdit()
        self.workflow_status.setMaximumHeight(80)
        self.workflow_status.setReadOnly(True)
        self.workflow_status.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        self.workflow_status.append("就绪")
        status_layout.addWidget(self.workflow_status)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                height: 22px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 3px;
            }
        """)
        self.progress.setValue(0)
        status_layout.addWidget(self.progress)
        
        right_layout.addWidget(status_group)
        

        # --- 剧情输入 ---
        plot_group = QGroupBox("📖 剧情输入")
        plot_group.setStyleSheet("""
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
        plot_layout = QVBoxLayout(plot_group)
        plot_layout.setSpacing(8)
        plot_layout.setContentsMargins(12, 12, 12, 12)
        
        # 剧情文本框
        self.plot_text = QTextEdit()
        self.plot_text.setPlaceholderText("粘贴或输入小说剧情，系统会自动分割成场景并生成视频...")
        self.plot_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-size: 12px;
                min-height: 200px;
            }
            QTextEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        plot_layout.addWidget(self.plot_text)
        
        # 导入按钮
        import_layout = QHBoxLayout()
        
        self.btn_import_txt = QPushButton("📂 导入 TXT")
        self.btn_import_txt.setStyleSheet("""
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
        import_layout.addWidget(self.btn_import_txt)
        
        self.btn_clear_plot = QPushButton("🗑️ 清空")
        self.btn_clear_plot.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        import_layout.addWidget(self.btn_clear_plot)
        import_layout.addStretch()
        plot_layout.addLayout(import_layout)
        
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
        preview_group = QGroupBox("🖼️ 预览")
        preview_group.setStyleSheet("""
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
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(8)
        preview_layout.setContentsMargins(12, 12, 12, 12)
        
        self.preview_label = QLabel("暂无预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fafafa;
                color: #888;
                font-size: 13px;
            }
        """)
        self.preview_label.setMinimumSize(320, 200)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_label.setScaledContents(True)
        preview_layout.addWidget(self.preview_label)
        
        bottom_splitter.addWidget(preview_group)
        
        # 日志区域
        log_group = QGroupBox("📝 日志")
        log_group.setStyleSheet("""
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
        log_layout = QVBoxLayout(log_group)
        log_layout.setSpacing(8)
        log_layout.setContentsMargins(12, 12, 12, 12)
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(180)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                font-family: Consolas, Monaco, monospace;
                font-size: 11px;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        log_layout.addWidget(self.log_area)
        
        bottom_splitter.addWidget(log_group)
        
        # 设置分割比例
        bottom_splitter.setSizes([350, 220])
        
        right_layout.addWidget(bottom_splitter)
        
        splitter.addWidget(right_panel)
        
        # 设置左右面板比例
        splitter.setSizes([350, 1050])
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #d0d0d0;
                font-size: 11px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("NovelVision Pro - 小说人物视频生成器")
    
    def update_window_title(self):
        try:
            import version
            build_info = f"(build: {version.BUILD_RUN_NUMBER}, {version.BUILD_COMMIT_SHA[:7]})"
            self.setWindowTitle(f"NovelVision Pro {build_info}")
        except:
            pass

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
        
        # 从剧情文本生成场景
        plot = self.plot_text.toPlainText().strip()
        if not plot:
            QMessageBox.warning(self, "警告", "请输入剧情内容。")
            return
        
        # 将剧情按段落分割成场景
        scenes = self.split_plot_into_scenes(plot)
        self.workflow.project_data["scenes"] = []
        for i, desc in enumerate(scenes):
            scene = self.workflow.add_scene(desc)
            self.workflow.project_data["scenes"].append(scene)
        
        if not self.workflow.project_data["scenes"]:
            QMessageBox.warning(self, "警告", "未能从剧情中分割出场景。")
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
    
    def open_about(self):
        dlg = AboutDialog(self)
        dlg.exec_()



    def import_txt(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "导入 TXT 文件", "", "Text Files (*.txt);;All Files (*)"
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.plot_text.setPlainText(content)
                self.log_area.append(f"📂 导入文件成功: {filepath}")
            except Exception as e:
                QMessageBox.warning(self, "导入失败", f"无法读取文件: {str(e)}")
    
    def clear_plot(self):
        self.plot_text.clear()
        self.log_area.append("🗑️ 剧情已清空")

    def split_plot_into_scenes(self, plot):
        """将剧情分割成场景列表"""
        # 先按空行分割
        paragraphs = [p.strip() for p in plot.split('\n\n') if p.strip()]
        
        # 如果没有空行，按句号/换行分割
        if len(paragraphs) <= 1:
            paragraphs = [p.strip() for p in plot.replace('。', '。\n').split('\n') if p.strip()]
        
        # 限制每个场景不要太长，超过200字再按逗号/分号切分
        scenes = []
        for p in paragraphs:
            if len(p) <= 300:
                scenes.append(p)
            else:
                import re
                parts = re.split(r'[，；？！]', p)
                current = ""
                for part in parts:
                    if len(current) + len(part) < 300:
                        current += part + "，"
                    else:
                        if current:
                            scenes.append(current.rstrip('，；'))
                        current = part + "，"
                if current:
                    scenes.append(current.rstrip('，；'))
        
        return scenes if scenes else [plot[:500]]

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用调色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 248))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(44, 62, 80))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(44, 62, 80))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # 设置应用字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    window = NovelVisionGUI()
    window.show()
    sys.exit(app.exec_())
