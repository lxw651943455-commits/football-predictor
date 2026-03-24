@echo off
echo ===============================================
echo   足球预测系统 - 一键分享给朋友
echo ===============================================
echo.
echo 正在启动公网分享...
echo.
echo 【注意】
echo 1. 请确保所有服务已启动（前端、后端、Python引擎）
echo 2. 分享链接会显示在下方
echo 3. 按 Ctrl+C 可以停止分享
echo 4. 停止分享不影响本地使用
echo.
echo ===============================================
echo.

REM 使用 expose 分享前端和后端
expose 3001 5000 --subdomain=my-football-predictor

echo.
echo 分享已停止
pause
