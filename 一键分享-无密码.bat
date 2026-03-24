@echo off
chcp 65001 >nul
echo ===============================================
echo   超简单公网分享 - 无需密码版本
echo ===============================================
echo.
echo 正在启动公网分享...
echo.
echo 【重要】
echo - 下面会显示一个网址
echo - 直接复制网址发给朋友
echo - 朋友打开就能访问，无需密码
echo - 按 Ctrl+C 停止分享
echo.
echo ===============================================
echo.
echo 正在连接 serveo...
echo.

REM 使用 serveo（需要 Git Bash，但通常 Windows 都有）
bash -c "ssh -R 80:localhost:3001 serveo.net"

pause
