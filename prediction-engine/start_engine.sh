#!/bin/bash
# Football Prediction Engine - Startup Script
# 确保环境变量正确加载

cd "$(dirname "$0")"

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 加载环境变量
export $(grep -v '^#' ../.env | xargs)

# 启动 Flask 服务器
echo "Starting Football Prediction Engine..."
echo "Environment loaded from ../.env"
python main.py
