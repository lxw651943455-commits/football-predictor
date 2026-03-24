@echo off
chcp 65001 >nul
cls
echo ===============================================
echo   足球预测系统 - 公网分享
echo ===============================================
echo.
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  请按照下面的步骤操作，5 分钟就能搞定              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 【第 1 步】注册 ngrok（免费）
echo.
echo 1. 按任意键打开注册页面...
pause >nul
start https://ngrok.com/signup
echo.
echo   ✓ 注册完成后，按任意键继续...
pause >nul
echo.
echo ===============================================
echo.
echo 【第 2 步】下载 ngrok
echo.
echo 1. 登后登录 ngrok
echo 2. 点击左侧菜单 "Your Account"
echo.
echo   ╔══════════════════════════════════════════════════════════╗
echo   ║ 2. 找到 "Download ngrok for Windows"                 ║
echo   ║ 3. 点击下载（下载 ngrok-stable-windows-amd64.zip）    ║
echo   ╚══════════════════════════════════════════════════════════╝
echo.
echo   下载完成后，按任意键继续...
pause >nul
echo.
echo ===============================================
echo.
echo 【第 3 步】解压 ngrok
echo.
echo 1. 找到下载的 .zip 文件
echo 2. 右键 → 解压到
echo 3. 选择文件夹，例如：C:\ngrok\
echo.
echo   解压完成后，按任意键继续...
pause >nul
echo.
echo ===============================================
echo.
echo 【第 4 步】启动分享
echo.
echo 1. 打开文件夹 C:\ngrok\
echo 2. 双击 ngrok.exe
echo 3. 会弹出一个命令行窗口
echo.
echo   ╔══════════════════════════════════════════════════════════╗
echo   ║ 4. 在窗口中输入：ngrok http 3001                     ║
echo   ║ 5. 按回车                                            ║
echo   ╚══════════════════════════════════════════════════════════╝
echo.
echo   窗口中会显示：
echo.
echo   Forwarding:
echo   https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:3001
echo.
echo   【重要】复制 https://xxxx.ngrok-free.app 这个地址！
echo.
echo ===============================================
echo.
echo.
echo 完成后，把 https://xxxx.ngrok-free.app 发给朋友
echo 朋友打开这个网址就能使用你的预测系统了！
echo.
echo 停止分享：关闭 ngrok 窗口即可
echo.
pause
