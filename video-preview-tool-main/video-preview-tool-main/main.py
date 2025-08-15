import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QScrollArea, QGridLayout, QSlider, QLineEdit,
                            QFrame, QStyle, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor, QPixmap, QImage
import vlc
import os

# 设置VLC路径
os.environ['VLC_PLUGIN_PATH'] = r'C:\Program Files (x86)\VideoLAN\VLC\plugins'
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
from typing import List, Dict
import random
from datetime import datetime
from video_player import VideoPlayer
import time

class CustomButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051FF;
            }
            QPushButton:pressed {
                background-color: #0041CC;
            }
        """)

class CustomSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #E5E5EA;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #007AFF;
                border: none;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #007AFF;
            }
        """)

class VideoPreviewWidget(QFrame):
    def __init__(self, video_path: str, display_name: str = None):
        super().__init__()
        self.video_path = video_path
        self.display_name = display_name or os.path.basename(video_path)
        self.selected = False
        
        # 设置图标路径 - 使用相对路径或默认图标
        self.icons_path = os.path.join(os.path.dirname(__file__), "images")
        # 如果图标目录不存在，使用系统默认图标
        if not os.path.exists(self.icons_path):
            self.icons_path = ""
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置整体样式
        self.setFixedSize(490, 340)
        self.setObjectName("videoCard")
        self.setStyleSheet("""
            #videoCard {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 12px;
                transform: scale(1.0);
                transition: all 0.2s ease-in-out;
            }
            #videoCard[selected="true"] {
                background: #F0F9F4;
                border: 2px solid #42B883;
                border-radius: 12px;
                transform: scale(1.1);
                box-shadow: 0 8px 16px rgba(66, 184, 131, 0.2);
            }
        """)
        
        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部标题栏
        title_container = QWidget()
        title_container.setFixedHeight(35)
        title_container.setObjectName("titleContainer")
        title_container.setStyleSheet("""
            #titleContainer {
                background: #F5F5F5;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
            #titleContainer[selected="true"] {
                background: #E8F5F0;
            }
        """)
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(12, 0, 12, 0)
        title_layout.setSpacing(8)
        
        # 文件名编辑框和编辑图标容器
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(4)
        
        # 文件名编辑框
        self.name_edit = QLineEdit(self.display_name)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #333333;
                font-size: 14px;
                padding: 0;
            }
            QLineEdit[selected="true"] {
                color: #42B883;
                font-weight: bold;
            }
            QLineEdit:focus {
                background: white;
                border: 1px solid #42B883;
                border-radius: 4px;
                padding: 0 4px;
            }
        """)
        self.name_edit.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.name_edit.setReadOnly(True)  # 默认设置为只读
        
        # 编辑图标
        edit_btn = QPushButton()
        edit_btn.setFixedSize(16, 16)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.icons_path:
            edit_btn.setIcon(QIcon(os.path.join(self.icons_path, "edit.png")))
        else:
            edit_btn.setText("✏")
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
        """)
        edit_btn.clicked.connect(self.start_edit)  # 连接点击事件
        
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(edit_btn)
        
        # 右侧按钮容器
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # 选择按钮
        self.select_btn = QPushButton()
        self.select_btn.setFixedSize(16, 16)
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.clicked.connect(self.toggle_select)
        self.update_select_button()
        
        # 删除按钮（使用关闭图标）
        close_btn = QPushButton()
        close_btn.setFixedSize(16, 16)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.icons_path:
            close_btn.setIcon(QIcon(os.path.join(self.icons_path, "close.png")))
        else:
            close_btn.setText("✕")
        close_btn.setIconSize(QSize(16, 16))
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
        """)
        close_btn.clicked.connect(self.delete_video)
        
        right_layout.addWidget(self.select_btn)
        right_layout.addWidget(close_btn)
        
        title_layout.addWidget(name_container)
        title_layout.addStretch()  # 添加弹性空间
        title_layout.addWidget(right_container)
        layout.addWidget(title_container)
        
        # 创建预览区域
        self.preview = QLabel()
        self.preview.setFixedSize(490, 270)
        self.preview.setStyleSheet("background: black; border: none;")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview)
        
        # 创建播放组件区域
        controls_container = QWidget()
        controls_container.setFixedHeight(35)
        controls_container.setStyleSheet("background: white; border-radius: 0 0 12px 12px;")
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(12, 0, 12, 0)
        controls_layout.setSpacing(10)
        
        # 播放按钮
        self.play_button = QPushButton()
        self.play_button.setFixedSize(24, 24)
        self.play_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.icons_path:
            self.play_button.setIcon(QIcon(os.path.join(self.icons_path, "play.png")))
        else:
            self.play_button.setText("▶")
        self.play_button.setIconSize(QSize(24, 24))
        self.play_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        
        # 进度条
        self.progress = QSlider(Qt.Orientation.Horizontal)
        self.progress.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #E0E0E0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
                background: #42B883;
            }
            QSlider::sub-page:horizontal {
                background: #42B883;
                border-radius: 2px;
            }
        """)
        
        # 时间显示标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.time_label.setFixedWidth(90)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(5)
        
        self.volume_button = QPushButton()
        self.volume_button.setFixedSize(24, 24)
        self.volume_button.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.icons_path:
            self.volume_button.setIcon(QIcon(os.path.join(self.icons_path, "volume.png")))
        else:
            self.volume_button.setText("🔊")
        self.volume_button.setIconSize(QSize(24, 24))
        self.volume_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(60)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #E0E0E0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
                background: #42B883;
            }
            QSlider::sub-page:horizontal {
                background: #42B883;
                border-radius: 2px;
            }
        """)
        self.volume_slider.setValue(100)
        
        # 播放速度按钮
        self.speed_button = QPushButton("1.0x")
        self.speed_button.setFixedSize(40, 24)
        self.speed_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                color: #666666;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.05);
            }
        """)
        
        # 将控件添加到播放组件布局
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.progress, 1)  # 进度条占据剩余空间
        controls_layout.addWidget(self.time_label)
        controls_layout.addWidget(self.volume_button)
        controls_layout.addWidget(self.volume_slider)
        controls_layout.addWidget(self.speed_button)
        
        # 将播放组件区域添加到主布局
        layout.addWidget(controls_container)
        
        # 创建播放器
        self.player = VideoPlayer(self.video_path, self.preview)
        
        # 连接信号
        self.play_button.clicked.connect(self.toggle_play)
        self.progress.sliderMoved.connect(self.seek)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.name_edit.editingFinished.connect(self.update_display_name)
        self.speed_button.clicked.connect(self.toggle_speed)
        
        # 设置定时器更新进度
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_progress)
        self.update_timer.start(1000)  # 每秒更新一次
        
        # 添加鼠标点击事件
        self.mousePressEvent = self.on_click
        
    def update_select_button(self):
        """更新选择按钮的样式"""
        self.select_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1.5px solid #CCCCCC;
                background-color: transparent;
                border-radius: 8px;
            }}
            QPushButton[selected="true"] {{
                border: none;
                background-image: url("{os.path.join(self.icons_path, 'check.png') if self.icons_path else ''}");
                background-position: center;
                background-repeat: no-repeat;
                background-color: #42B883;
            }}
            QPushButton:hover {{
                border-color: #42B883;
            }}
        """)
        self.select_btn.setProperty("selected", self.selected)
        self.select_btn.style().unpolish(self.select_btn)
        self.select_btn.style().polish(self.select_btn)
        
    def toggle_select(self):
        """切换选中状态"""
        self.selected = not self.selected
        self.setProperty("selected", self.selected)
        self.name_edit.setProperty("selected", self.selected)
        
        # 更新标题栏的选中状态
        title_container = self.findChild(QWidget, "titleContainer")
        if title_container:
            title_container.setProperty("selected", self.selected)
            title_container.style().unpolish(title_container)
            title_container.style().polish(title_container)
        
        self.update_select_button()
        self.style().unpolish(self)
        self.style().polish(self)
        self.name_edit.style().unpolish(self.name_edit)
        self.name_edit.style().polish(self.name_edit)
        
    def on_click(self, event):
        """处理鼠标点击事件"""
        self.toggle_select()
        
    def toggle_speed(self):
        """切换播放速度"""
        speeds = [1.0, 1.5, 2.0]
        current_speed = float(self.speed_button.text().replace('x', ''))
        next_speed = speeds[(speeds.index(current_speed) + 1) % len(speeds)]
        self.speed_button.setText(f"{next_speed}x")
        self.player.set_playback_speed(next_speed)
        
    def toggle_play(self):
        if not self.player.is_playing:
            self.player.play()
            if self.icons_path:
                self.play_button.setIcon(QIcon(os.path.join(self.icons_path, "pause.png")))
            else:
                self.play_button.setText("⏸")
            self.update_timer.start()
        else:
            self.player.pause()
            if self.icons_path:
                self.play_button.setIcon(QIcon(os.path.join(self.icons_path, "play.png")))
            else:
                self.play_button.setText("▶")
            self.update_timer.stop()
            
    def seek(self, value):
        self.player.seek(value)
        
    def set_volume(self, value):
        """设置音量"""
        self.player.set_volume(value)
        
    def update_progress(self):
        """更新进度条和时间显示"""
        if self.player.is_playing:
            current_time = self.player.get_time()
            total_time = self.player.get_duration()
            if total_time > 0:
                # 更新进度条
                self.progress.setValue(int(current_time * 100 / total_time))
                
                # 更新时间显示
                current_str = time.strftime("%M:%S", time.gmtime(current_time/1000))
                total_str = time.strftime("%M:%S", time.gmtime(total_time/1000))
                self.time_label.setText(f"{current_str} / {total_str}")
                
    def start_edit(self):
        """开始编辑文件名"""
        self.name_edit.setReadOnly(False)  # 允许编辑
        self.name_edit.setFocus()  # 设置焦点
        # 选中文件名（不包括扩展名）
        name, ext = os.path.splitext(self.name_edit.text())
        self.name_edit.setSelection(0, len(name))
        
    def update_display_name(self):
        """更新显示名称"""
        if not self.name_edit.isReadOnly():  # 只在编辑模式下更新
            new_name = self.name_edit.text()
            # 确保有扩展名
            if not os.path.splitext(new_name)[1]:
                _, ext = os.path.splitext(self.display_name)
                new_name += ext
            self.display_name = new_name
            self.name_edit.setText(new_name)
        self.name_edit.setReadOnly(True)  # 恢复只读状态
        
    def delete_video(self):
        """从界面中移除视频卡片（不删除实际文件）"""
        self.player.cleanup()
        self.deleteLater()
        # 发送信号通知主窗口更新布局
        parent = self.parent()
        if parent and hasattr(parent, 'update_grid_layout'):
            parent.update_grid_layout()
        
    def get_current_info(self):
        """获取当前视频信息"""
        return {
            'original_path': self.video_path,
            'display_name': self.display_name,
            'selected': self.selected
        }
        
    def closeEvent(self, event):
        self.player.cleanup()
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频预览工具")
        self.setMinimumSize(1200, 800)
        self.videos = []
        self.selected_videos = []
        self.movie_quotes = [
            "生活就像巧克力盒，你永远不知道下一颗是什么味道。 —《阿甘正传》",
            "希望是好事，也许是最好的，好事不会消亡。 —《肖申克的救赎》",
            "不要让任何人告诉你，你做不到什么事。 —《当幸福来敲门》",
            "每个人都死，但不是每个人都真正活过。 —《勇敢的心》",
            "我们每个人都是自己的命运的建筑师。 —《盗梦空间》",
            "有时候，最重要的不是你去了哪里，而是和谁一起去。 —《泰坦尼克号》",
            "伟大的力量必须承担伟大的责任。 —《蜘蛛侠》",
            "人生不是等待暴风雨过去，而是学会在雨中跳舞。 —《肖申克的救赎》",
            "有些鸟儿是关不住的，因为它们的羽毛太亮了。 —《肖申克的救赎》",
            "我们的生命是一场马拉松，不是短跑。 —《唐人街探案》",
            "不要因为走得太远，就忘记了为什么出发。 —《星际穿越》",
            "世界上最宝贵的不是金钱和权力，而是时间。 —《盗梦空间》",
            "人生最大的失败，就是放弃。 —《海上钢琴师》",
            "没有人能够回到过去重新开始，但谁都可以从现在开始，书写一个全新的结局。 —《本杰明·巴顿奇事》",
            "生活中最困难的不是做出选择，而是坚持选择。 —《教父》"
        ]
        self.current_quote_index = 0
        self.is_all_selected = False
        self.setup_ui()
        
        # 启动台词自动切换定时器
        self.quote_timer = QTimer(self)
        self.quote_timer.timeout.connect(self.update_quote)
        self.quote_timer.start(10000)  # 每10秒切换一次
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(20)
        
        # 顶部区域（台词展示和按钮）
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(10, 0, 10, 0)
        
        # 电影台词
        quote_container = QWidget()
        quote_layout = QVBoxLayout(quote_container)
        quote_layout.setContentsMargins(0, 0, 0, 0)
        self.quote_label = QLabel(self.movie_quotes[0])
        self.quote_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-size: 20px;
                font-style: italic;
                font-weight: normal;
            }
        """)
        self.quote_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.quote_label.setWordWrap(True)
        quote_layout.addWidget(self.quote_label)
        top_layout.addWidget(quote_container, stretch=1)
        
        # 按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        # 上传按钮
        upload_btn = QPushButton("上传")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4B8BF4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #3B7DE3;
            }
        """)
        upload_btn.clicked.connect(self.add_videos)
        button_layout.addWidget(upload_btn)
        
        # 移动到按钮
        move_btn = QPushButton("移动到")
        move_btn.setStyleSheet("""
            QPushButton {
                background-color: #42B883;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 24px;
                font-size: 14px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #3AA876;
            }
        """)
        move_btn.clicked.connect(self.move_videos)
        button_layout.addWidget(move_btn)
        
        # 全选按钮
        select_all_btn = QPushButton()
        select_all_btn.setIcon(QIcon.fromTheme("edit-select-all"))
        select_all_btn.setFixedSize(32, 32)
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(66, 184, 131, 0.1);
            }
            QPushButton[selected="true"] {
                background-color: rgba(66, 184, 131, 0.2);
            }
        """)
        select_all_btn.clicked.connect(self.toggle_select_all)
        button_layout.addWidget(select_all_btn)
        self.select_all_btn = select_all_btn  # 保存引用以便后续使用
        
        top_layout.addWidget(button_container)
        layout.addWidget(top_frame)
        
        # 视频网格区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: none;
            }
            QWidget#gridWidget {
                background-color: white;
            }
        """)
        
        self.grid_widget = QWidget()
        self.grid_widget.setObjectName("gridWidget")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_area.setWidget(self.grid_widget)
        
        layout.addWidget(self.scroll_area)
        
        # 空状态提示
        self.empty_state = QFrame()
        self.empty_state.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px dashed #E0E0E0;
                border-radius: 4px;
                min-height: 300px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: rgba(75, 139, 244, 0.1);
                border-radius: 40px;
            }
        """)
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 上传图标按钮
        upload_icon_btn = QPushButton()
        upload_icon_btn.setIcon(QIcon.fromTheme("document-open"))
        upload_icon_btn.setIconSize(QSize(48, 48))
        upload_icon_btn.clicked.connect(self.add_videos)
        empty_layout.addWidget(upload_icon_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.grid_layout.addWidget(self.empty_state, 0, 0)
        
    def add_videos(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov);;所有文件 (*.*)"
        )
        
        if files:
            if len(files) + len(self.videos) > 50:
                QMessageBox.warning(self, "警告", "视频数量不能超过50个！")
                return
                
            # 隐藏空状态提示
            self.empty_state.hide()
            
            # 添加视频到列表开头
            for file in reversed(files):  # 反转顺序添加，保证最后选择的文件显示在最前面
                self.add_video_widget(file, insert_at_beginning=True)
                
    def add_video_widget(self, file_path, insert_at_beginning=False):
        video_widget = VideoPreviewWidget(file_path)
        
        if insert_at_beginning:
            # 将所有现有视频向后移动
            self.videos.insert(0, {
                "widget": video_widget,
                "path": file_path
            })
        else:
            # 添加到末尾
            self.videos.append({
                "widget": video_widget,
                "path": file_path
            })
            
        # 重新排列所有视频
        self.rearrange_videos()
            
    def rearrange_videos(self):
        # 临时存储所有视频部件
        widgets = []
        for video in self.videos:
            widget = video["widget"]
            # 从布局中移除但不删除部件
            self.grid_layout.removeWidget(widget)
            widgets.append(widget)
            
        # 重新添加到网格布局
        for i, widget in enumerate(widgets):
            row = i // 3
            col = i % 3
            self.grid_layout.addWidget(widget, row, col)
            
    def delete_video(self, widget):
        # 从视频列表中移除
        for video in self.videos[:]:
            if video["widget"] == widget:
                self.videos.remove(video)
                break
                
        # 重新排列剩余视频
        self.rearrange_videos()
        
        # 如果没有视频了，显示空状态
        if not self.videos:
            self.empty_state.show()
            
    def toggle_select_all(self):
        """切换全选状态"""
        self.is_all_selected = not self.is_all_selected
        self.select_all_btn.setProperty("selected", self.is_all_selected)
        self.select_all_btn.style().unpolish(self.select_all_btn)
        self.select_all_btn.style().polish(self.select_all_btn)
        
        # 更新所有视频卡片的选中状态
        for video in self.videos:
            widget = video["widget"]
            widget.selected = self.is_all_selected
            
            # 更新卡片状态
            widget.setProperty("selected", self.is_all_selected)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            
            # 更新文件名状态
            widget.name_edit.setProperty("selected", self.is_all_selected)
            widget.name_edit.style().unpolish(widget.name_edit)
            widget.name_edit.style().polish(widget.name_edit)
            
            # 更新标题栏状态
            title_container = widget.findChild(QWidget, "titleContainer")
            if title_container:
                title_container.setProperty("selected", self.is_all_selected)
                title_container.style().unpolish(title_container)
                title_container.style().polish(title_container)
            
            # 更新选择按钮状态
            widget.update_select_button()
            
    def move_videos(self):
        """复制选中的视频到新位置"""
        selected_widgets = [v for v in self.videos if v["widget"].selected]
        if not selected_widgets:
            # 使用QMessageBox创建更现代的提示框
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("提示")
            msg.setText("请选择要移动的视频")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #333333;
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton {
                    background-color: #42B883;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 24px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #3AA876;
                }
            """)
            msg.exec()
            return
            
        # 选择目标文件夹
        target_dir = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if not target_dir:
            return
            
        try:
            for video in selected_widgets:
                widget = video["widget"]
                info = widget.get_current_info()
                
                # 使用显示名称作为新的文件名
                new_name = info['display_name']
                if not os.path.splitext(new_name)[1]:  # 如果没有扩展名，使用原文件扩展名
                    _, ext = os.path.splitext(info['original_path'])
                    new_name = new_name + ext
                    
                new_path = os.path.join(target_dir, new_name)
                
                # 处理文件名冲突
                base, ext = os.path.splitext(new_path)
                counter = 1
                while os.path.exists(new_path):
                    new_path = f"{base}_{counter}{ext}"
                    counter += 1
                
                # 复制文件
                import shutil
                shutil.copy2(info['original_path'], new_path)
                
                # 更新UI状态
                widget.selected = False
                widget.setProperty("selected", False)
                widget.style().unpolish(widget)
                widget.style().polish(widget)
            
            QMessageBox.information(self, "成功", f"已将选中的视频复制到：{target_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制文件时出错：{str(e)}")
            
    def update_quote(self):
        """更新电影台词"""
        self.current_quote_index = (self.current_quote_index + 1) % len(self.movie_quotes)
        self.quote_label.setText(self.movie_quotes[self.current_quote_index])

    def update_grid_layout(self):
        """更新网格布局"""
        # 移除所有部件
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 重新添加视频卡片
        row = 0
        col = 0
        max_cols = 3
        
        for video in self.videos:
            if video["widget"].parent():  # 检查部件是否仍然有效
                self.grid_layout.addWidget(video["widget"], row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
        # 如果没有视频，显示空状态
        if not self.videos:
            self.empty_state.show()
        else:
            self.empty_state.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())