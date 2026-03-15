#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QSplitter,
    QFileDialog, QMessageBox, QProgressBar, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import os
from core.image_gen import ImageGenWorker
from core.tts import TTSWorker
from core.video_composer import VideoComposerWorker
from core.workflow import WorkflowManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovelVision Pro - 小说人物视频生成器")
        self.resize(1200, 800)
        self.setup_ui()
        self.workflow = WorkflowManager()
        self.workers = []
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 顶部：项目管理栏
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.addWidget(QLabel("项目:"))
        self.project_name = QLineEdit("新项目")
        top_layout.addWidget(self.project_name)
        self.btn_new = QPushButton("新建")
        self.btn_save = QPushButton("保存")
        self.btn_load = QPushButton("加载")
        top_layout.addWidget(self.btn_new)
        top_layout.addWidget(self.btn_save)
        top_layout.addWidget(self.btn_load)
        top_layout.addStretch()
        layout.addWidget(top_bar)
        
        # 中部：分割区域（左侧角色/素材，右侧工作流）
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板：角色与描述
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("角色设定"))
        self.char_list = QListWidget()
        left_layout.addWidget(self.char_list)
        self.char_desc = QTextEdit()
        self.char_desc.setPlaceholderText("输入人物描述，例如:\n- 姓名、年龄、外貌\n- 性格特点\n- 服装风格")
        left_layout.addWidget(QLabel("描述"))
        left_layout.addWidget(self.char_desc)
        self.btn_add_char = QPushButton("添加角色")
        self.btn_gen_image = QPushButton("生成图像")
        left_layout.addWidget(self.btn_add_char)
        left_layout.addWidget(self.btn_gen_image)
        splitter.addWidget(left_panel)
        
        # 中间面板：工作流控制
        mid_panel = QWidget()
        mid_layout = QVBoxLayout(mid_panel)
        mid_layout.addWidget(QLabel("工作流"))
        self.workflow_status = QListWidget()
        mid_layout.addWidget(self.workflow_status)
        self.btn_start = QPushButton("开始生成")
        self.btn_stop = QPushButton("停止")
        mid_layout.addWidget(self.btn_start)
        mid_layout.addWidget(self.btn_stop)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        mid_layout.addWidget(self.progress)
        splitter.addWidget(mid_panel)
        
        # 右侧面板：输出预览
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(QLabel("输出预览"))
        self.preview_label = QLabel("预览区域")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        right_layout.addWidget(self.preview_label)
        right_layout.addWidget(QLabel("日志"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        right_layout.addWidget(self.log_area)
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 300, 600])
        layout.addWidget(splitter)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 信号连接
        self.btn_new.clicked.connect(self.new_project)
        self.btn_save.clicked.connect(self.save_project)
        self.btn_load.clicked.connect(self.load_project)
        self.btn_add_char.clicked.connect(self.add_character)
        self.btn_gen_image.clicked.connect(self.generate_character_image)
        self.btn_start.clicked.connect(self.start_workflow)
        self.btn_stop.clicked.connect(self.stop_workflow)
        
    def new_project(self):
        self.project_name.setText("新项目")
        self.char_list.clear()
        self.char_desc.clear()
        self.log("已创建新项目")
        
    def save_project(self):
        # TODO: 实现项目保存
        self.log("项目保存功能开发中...")
        
    def load_project(self):
        # TODO: 实现项目加载
        self.log("项目加载功能开发中...")
        
    def add_character(self):
        desc = self.char_desc.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "提示", "请输入角色描述")
            return
        self.char_list.addItem(desc[:50] + ("..." if len(desc) > 50 else ""))
        self.char_desc.clear()
        self.log(f"添加角色: {desc[:30]}...")
        
    def generate_character_image(self):
        from core.image_gen import ImageGenWorker
        worker = ImageGenWorker(self.char_desc.toPlainText())
        worker.signals.finished.connect(self.on_image_generated)
        worker.signals.error.connect(self.on_worker_error)
        self.workers.append(worker)
        worker.start()
        self.log("正在生成角色图像...")
        
    def on_image_generated(self, image_path):
        self.log(f"图像生成完成: {image_path}")
        QMessageBox.information(self, "完成", f"图像已保存到: {image_path}")
        
    def on_worker_error(self, error_msg):
        self.log(f"错误: {error_msg}")
        QMessageBox.critical(self, "错误", error_msg)
        
    def start_workflow(self):
        self.log("启动工作流...")
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        # TODO: 调用工作流管理器
        self.workflow_status.addItem("开始生成流程")
        
    def stop_workflow(self):
        self.log("停止工作流")
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.workflow.stop()
        
    def check_workflow_status(self):
        # 定期检查工作流状态并更新进度
        pass
        
    def log(self, message):
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(f"[{time_str}] {message}")
        self.status_bar.showMessage(message)
        
    def preview_image(self, image_path):
        # TODO: 实现图片预览
        self.preview_label.setText(f"预览: {os.path.basename(image_path)}")