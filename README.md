# 视频预览工具 (Video Preview Tool)

一个基于 Python 和 PyQt6 开发的现代化视频预览和管理工具。

## 功能特点

- 🎬 支持多种视频格式（MP4、AVI、MKV、MOV）
- 📺 视频预览和播放功能
- ⚡ 批量视频导入和管理
- 🎯 视频文件快速移动/复制
- 🎨 现代化 UI 设计
- 🔄 支持视频播放速度调节（1.0x、1.5x、2.0x）
- 🔊 音量控制
- ✨ 优雅的动画效果

## 系统要求

- Python 3.8+
- Windows 10/11

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/你的用户名/video-preview-tool.git
cd video-preview-tool
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行程序：
```bash
python main.py
```

## 使用说明

1. **添加视频**
   - 点击"上传"按钮或拖拽视频文件到应用程序窗口
   - 支持批量导入视频文件

2. **视频预览**
   - 点击视频卡片上的播放按钮开始预览
   - 使用进度条控制播放进度
   - 调节音量和播放速度

3. **文件管理**
   - 点击视频卡片选择视频
   - 使用全选按钮批量选择
   - 点击"移动到"按钮将选中的视频移动到指定位置

4. **文件名编辑**
   - 点击视频卡片上的编辑图标修改文件名
   - 自动保留原文件扩展名

## 依赖项

- PyQt6
- python-vlc
- opencv-python
- Pillow

## 开发说明

项目使用 PyQt6 构建用户界面，python-vlc 处理视频播放，opencv-python 用于视频缩略图生成。

### 项目结构

```
video-preview-tool/
├── main.py              # 主程序入口
├── video_player.py      # 视频播放器组件
├── requirements.txt     # 项目依赖
├── images/             # 图标资源
│   ├── check.png
│   ├── close.png
│   ├── edit.png
│   ├── icon.png
│   ├── pause.png
│   ├── play.png
│   └── volume.png
└── README.md           # 项目文档
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。