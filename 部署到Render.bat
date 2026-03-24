@echo off
chcp 65001 >nul
cls
echo ===============================================
echo   足球预测 - Render 后端部署
echo ===============================================
echo.
echo 免费方案：Render.com (750小时/月)
echo.
echo 【步骤说明】
echo.
echo 1. 打开浏览器访问: https://dashboard.render.com
echo 2. 注册/登录账号（推荐用 GitHub 登录）
echo 3. 点击 "New +" → "Web Service"
echo 4. 连接 GitHub 仓库：football-predictor
echo 5. 配置如下：
echo    - Name: football-backend
echo    - Root Directory: backend
echo    - Build Command: npm install
echo    - Start Command: node server-simple.js
echo    - Plan: FREE
echo 6. 点击 "Create Web Service"
echo.
echo ===============================================
echo.
echo 部署完成后会得到一个 URL，格式类似：
echo https://football-backend.onrender.com
echo.
echo 然后需要更新前端的 API 地址！
echo.
echo ===============================================
echo.
pause

REM 打开 Render 控制台
start https://dashboard.render.com

echo.
echo 已打开浏览器，请按照上述步骤操作...
echo.
pause
