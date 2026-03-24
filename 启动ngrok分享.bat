@echo off
chcp 65001 >nul
echo ===============================================
echo   启动 ngrok 公网分享
echo ===============================================
echo.
echo 【前提】请先下载并安装 ngrok
echo.
if not exist "C:\ngrok\ngrok.exe" (
    echo ngrok 未安装！
    echo.
    echo 请先运行：下载ngrok.bat
    echo.
    pause
    exit /b
)

echo 正在启动 ngrok...
echo.

cd C:\ngrok
start ngrok.exe http 3001

echo.
echo ✅ ngrok 已启动！
echo.
echo 【使用说明】
echo 1. 查看弹出的命令行窗口
echo 2. 找到 Forwarding 这一行：
echo.
echo    Forwarding  https://xxxx.ngrok-free.app -> http://localhost:3001
echo.
echo 3. 复制 https://xxxx.ngrok-free.app 这个地址
echo.
echo 4. 发给朋友，他们就能访问了
echo.
echo 5. 关闭 ngrok 窗口就停止分享
echo.
pause
