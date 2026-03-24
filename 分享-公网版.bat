@echo off
chcp 65001 >nul
echo ===============================================
echo   使用 Cloudflare Tunnel 公网分享
echo ===============================================
echo.
echo 这个方案需要先安装 cloudflared
echo.
echo 【安装步骤】
echo.
echo 1. 下载 cloudflared：
echo    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
echo.
echo 2. 重命名为 cloudflared.exe
echo.
echo 3. 放到 C:\Program Files\cloudflared\
echo.
echo 4. 添加到系统 PATH
echo.
echo ===============================================
echo.
echo 【或者使用更简单的方案】
echo.
echo 双击运行：分享给朋友-简单版.bat
echo.
echo 这会显示你的本机 IP，
echo 朋友在同一个 Wi-Fi 下就能访问
echo.
pause
