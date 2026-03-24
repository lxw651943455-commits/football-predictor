#!/bin/bash

# Football Predictor - Stop Script
# Stops all running services

echo "Stopping Football Predictor services..."

# Check if using Docker
if docker-compose ps | grep -q "Up"; then
    echo "Stopping Docker containers..."
    docker-compose down
    echo "All services stopped"
else
    # Stop local processes
    if [ -f .engine.pid ]; then
        kill $(cat .engine.pid) 2>/dev/null
        rm .engine.pid
    fi

    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi

    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi

    # Also kill by port
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true

    echo "All services stopped"
fi
