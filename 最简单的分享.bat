@echo off
chcp 65001 >nul
echo ===============================================
echo   最简单的公网分享方案 - 一行命令搞定
echo ===============================================
echo.
echo 方案选择：
echo.
echo [1] 使用 npx localtunnel（推荐，无需注册）
echo [2] 使用 ngrok（需要注册账号）
echo.
set /p choice="请选择方案 (1 或 2): "

if "%choice%"=="1" goto :localtunnel
if "%choice%"=="2" goto :ngrok
echo 无效选择
pause
exit

:localtunnel
echo.
echo [方案 1] 正在使用 localtunnel...
echo.
echo 正在启动公网分享...
echo.
echo 【重要】
echo - 下面会显示一个网址，例如：https://xxx-3001.localtunnel.me
echo - 复制这个网址发给朋友
echo - 按 Ctrl+C 停止分享
echo.
timeout /t 3 >nul
npx localtunnel --port 3001 --subdomain my-football
goto :end

:ngrok
echo.
echo [方案 2] ngrok 需要先注册
echo.
echo 1. 访问 https://ngrok.com 注册
echo 2. 下载 ngrok for Windows
echo 3. 解压到任意目录
echo 4. 运行: ngrok http 3001
echo.
echo 注册页面会自动打开...
start https://ngrok.com
goto :end

:end
echo.
echo ===============================================
echo.
pause
