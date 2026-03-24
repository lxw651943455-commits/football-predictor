@echo off
chcp 65001 >nul
echo ===============================================
echo   足球预测系统 - 自动下载并启动公网分享
echo ===============================================
echo.

set CLOUDFLARED_URL=https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
set CLOUDFLARED_FILE=%TEMP%\cloudflared.exe

REM 检查是否已安装
where cloudflared >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [✓] cloudflared 已安装
    goto :run
)

echo [1/3] 正在下载 cloudflared...
echo.

REM 使用 PowerShell 下载
powershell -Command "& {Invoke-WebRequest -Uri '%CLOUDFLARED_URL%' -OutFile '%CLOUDFLARED_FILE%'}"

if not exist %CLOUDFLARED_FILE% (
    echo [✗] 下载失败
    echo.
    echo 请手动下载：
    echo %CLOUDFLARED_URL%
    echo.
    echo 保存为：cloudflared.exe
    echo.
    pause
    exit /b 1
)

echo [✓] 下载完成
echo.

:run
echo ===============================================
echo [2/3] 启动公网隧道...
echo ===============================================
echo.
echo 正在启动 Cloudflare Tunnel...
echo 会弹出两个窗口显示公网地址
echo.
echo 【重要】复制 https:// 开头的地址发给朋友
echo.
pause

REM 启动前端隧道
start "前端公网地址" cmd /k "%CLOUDFLARED_FILE% tunnel --url http://localhost:3001"

timeout /t 2 >nul

REM 启动后端隧道
start "后端公网地址" cmd /k "%CLOUDFLARED_FILE% tunnel --url http://localhost:5000"

echo.
echo [✓] 隧道已启动！
echo.
echo 【使用说明】
echo 1. 查看弹出的两个窗口
echo 2. 复制 https:// 开头的地址
echo 3. 发给朋友，他们就能访问了
echo 4. 关闭这两个窗口就停止分享
echo.
echo ===============================================
echo.
pause
