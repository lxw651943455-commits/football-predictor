@echo off
REM Football Prediction Engine - Windows Startup Script

cd /d "%~dp0prediction-engine"

echo Starting Football Prediction Engine...
echo Environment variables loaded from .env

REM 直接使用 python 运行，python-dotenv 会在 main.py 中加载
python main.py
