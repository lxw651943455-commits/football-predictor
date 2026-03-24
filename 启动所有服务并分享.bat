@echo off
echo ===============================================
echo   启动所有服务并分享
echo ===============================================
echo.

REM 启动后端
cd /d "%~dp0backend"
echo [1/3] 启动后端...
start "Backend Server" cmd /k "node server.js"
timeout /t 3 >nul

REM 启动 Python 引擎
cd /d "%~dp0prediction-engine"
echo [2/3] 启动 Python 引擎...
start "Python Engine" cmd /k "python main.py"
timeout /t 3 >nul

REM 启动前端
cd /d "%~dp0frontend"
echo [3/3] 启动前端...
start "Frontend" cmd /k "npm run dev"
timeout /t 5 >nul

echo.
echo ✅ 所有服务已启动！
echo.
echo 现在启动公网分享...
echo.

REM 启动分享
cd /d "%~dp0"
expose 3001 5000 --subdomain=my-football-predictor

pause
