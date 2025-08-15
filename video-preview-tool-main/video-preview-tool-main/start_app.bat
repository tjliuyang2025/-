@echo off
cd /d "%~dp0"
echo 正在启动视频预览工具...
py -3 main.py
if errorlevel 1 (
    echo.
    echo 程序运行出错！
    echo 可能的原因：
    echo 1. 未安装VLC媒体播放器
    echo 2. 缺少必要的依赖包
    echo.
    echo 请确保已安装VLC媒体播放器
    echo 下载地址：https://www.videolan.org/vlc/
    echo.
    pause
) else (
    echo.
    echo 程序已正常退出
    pause
) 