import vlc
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon
import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
from typing import Optional, Callable
import time
import platform
import numpy as np

class VideoPlayer:
    def __init__(self, video_path: str, preview_widget: QLabel):
        self.video_path = video_path
        self.preview_widget = preview_widget
        self.is_playing = False
        self.playback_speed = 1.0
        
        # 创建VLC实例和播放器
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(self.video_path)
        self.player.set_media(self.media)
        
        # 设置播放窗口
        if platform.system() == "Windows":
            self.player.set_hwnd(int(self.preview_widget.winId()))
        elif platform.system() == "Darwin":  # macOS
            self.player.set_nsobject(int(self.preview_widget.winId()))
        else:  # Linux
            self.player.set_xwindow(self.preview_widget.winId())
            
        # 设置视频输出比例
        self.player.video_set_scale(0)  # 0表示自动缩放
        self.player.video_set_aspect_ratio("16:9")  # 设置默认比例
        
        # 加载缩略图
        self.load_thumbnail()
        
    def play(self):
        """开始播放"""
        if not self.is_playing:
            self.player.play()
            self.is_playing = True
            
    def pause(self):
        """暂停播放"""
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            
    def stop(self):
        """停止播放"""
        self.player.stop()
        self.is_playing = False
        self.load_thumbnail()  # 显示缩略图
        
    def seek(self, position: float):
        """设置播放位置（0-100）"""
        self.player.set_position(position / 100.0)
        
    def set_volume(self, volume: float):
        """设置音量（0-100）"""
        self.player.audio_set_volume(int(volume))
        
    def get_position(self) -> float:
        """获取当前播放位置（0-100）"""
        return self.player.get_position() * 100
        
    def cleanup(self):
        """清理资源"""
        self.stop()
        self.player.release()
        self.instance.release()
        
    def load_thumbnail(self):
        """加载视频缩略图"""
        try:
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            if ret:
                # 获取视频的原始尺寸
                video_h, video_w = frame.shape[:2]
                preview_w = self.preview_widget.width()
                preview_h = self.preview_widget.height()
                
                # 计算缩放比例，保持宽高比
                scale = min(preview_w/video_w, preview_h/video_h)
                new_w = int(video_w * scale)
                new_h = int(video_h * scale)
                
                # 调整帧大小
                frame = cv2.resize(frame, (new_w, new_h))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 创建一个黑色背景
                background = np.zeros((preview_h, preview_w, 3), dtype=np.uint8)
                
                # 计算居中位置
                y_offset = (preview_h - new_h) // 2
                x_offset = (preview_w - new_w) // 2
                
                # 将调整后的帧放在黑色背景上
                background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = frame
                
                # 转换为QPixmap并显示
                image = QImage(background.data, preview_w, preview_h, background.strides[0], QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.preview_widget.setPixmap(pixmap)
            cap.release()
        except Exception as e:
            print(f"Error loading thumbnail: {str(e)}")
            
    def set_playback_speed(self, speed: float):
        """设置播放速度"""
        self.player.set_rate(speed)
        self.playback_speed = speed

    def get_time(self):
        """获取当前播放时间（毫秒）"""
        return self.player.get_time()
        
    def get_duration(self):
        """获取视频总时长（毫秒）"""
        return self.player.get_length()

class VideoPlayerTk:
    def __init__(self, video_path: str, preview_label: tk.Label):
        self.video_path = video_path
        self.preview_label = preview_label
        self.cap = cv2.VideoCapture(video_path)
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.thread: Optional[threading.Thread] = None
        self.on_frame_update: Optional[Callable] = None
        self.volume = 0.5  # 默认音量
        
    def play(self):
        if not self.is_playing:
            self.is_playing = True
            self.thread = threading.Thread(target=self._play_video)
            self.thread.daemon = True
            self.thread.start()
            
    def pause(self):
        self.is_playing = False
        
    def seek(self, position: float):
        """设置视频播放位置（0-100）"""
        frame_no = int((position / 100) * self.total_frames)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        self.current_frame = frame_no
        
    def set_volume(self, volume: float):
        """设置音量（0-100）"""
        self.volume = volume / 100.0
        
    def _play_video(self):
        while self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
                
            # 调整帧大小以适应预览区域
            height, width = frame.shape[:2]
            preview_width = self.preview_label.winfo_width()
            preview_height = self.preview_label.winfo_height()
            
            # 计算缩放比例
            scale = min(preview_width/width, preview_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # 调整大小
            frame = cv2.resize(frame, (new_width, new_height))
            
            # 转换颜色空间
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为PhotoImage
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            
            # 更新预览
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            
            # 更新当前帧
            self.current_frame += 1
            
            # 控制播放速度
            time.sleep(1/self.fps)
            
    def get_current_position(self) -> float:
        """获取当前播放位置（0-100）"""
        return (self.current_frame / self.total_frames) * 100
        
    def release(self):
        """释放资源"""
        self.is_playing = False
        if self.thread:
            self.thread.join()
        self.cap.release() 