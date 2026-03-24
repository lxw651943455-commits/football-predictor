@echo off
chcp 65001 >/dev/null
cls
echo ===============================================
echo   一键公网分享 - 无需注册
echo ===============================================
echo.
echo 正在启动公网隧道...
echo.
echo 【重要】
echo - 下面会要求你输入 yes 确认
echo - 确认后会显示一个网址
echo - 复制那个网址发给朋友
echo.
echo 按 Ctrl+C 停止分享
echo.
echo ===============================================
echo.
bash -c "ssh -R 80:localhost:3001 -o StrictHostKeyChecking=no serveo.net"
pause
