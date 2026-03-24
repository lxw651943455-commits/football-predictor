#!/bin/bash

# Football Predictor - One-Command Startup Script
# This script sets up and starts all services

set -e

echo "================================"
echo "  Football Predictor - Startup"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo "  cp .env.example .env"
    echo "  # Edit .env and add your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required API keys
if [ -z "$THE_ODDS_API_KEY" ] || [ "$THE_ODDS_API_KEY" == "your_the_odds_api_key_here" ]; then
    echo -e "${YELLOW}Warning: THE_ODDS_API_KEY not configured${NC}"
    echo "You can get a free key at: https://api.the-odds-api.com/"
fi

if [ -z "$API_FOOTBALL_KEY" ] || [ "$API_FOOTBALL_KEY" == "your_api_football_key_here" ]; then
    echo -e "${YELLOW}Warning: API_FOOTBALL_KEY not configured${NC}"
    echo "Some features will be limited without API-Football"
    echo "You can get a free key at: https://api-football.com/register"
fi

echo -e "${GREEN}Environment check complete${NC}"
echo ""

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}Docker detected, starting with Docker Compose...${NC}"

    # Build and start containers
    docker-compose build
    docker-compose up -d

    echo ""
    echo -e "${GREEN}All services started!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:5000"
    echo "  API Docs:  http://localhost:5000/health"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop:"
    echo "  docker-compose down"

else
    # Docker not available, run locally
    echo -e "${YELLOW}Docker not detected, starting services locally...${NC}"
    echo ""

    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Error: Node.js is not installed${NC}"
        echo "Please install Node.js 18+ from: https://nodejs.org/"
        exit 1
    fi

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        echo "Please install Python 3.8+ from: https://python.org/"
        exit 1
    fi

    echo -e "${GREEN}All dependencies found${NC}"
    echo ""

    # Install backend dependencies
    echo "Installing backend dependencies..."
    cd backend
    npm install
    cd ..

    # Install prediction engine dependencies
    echo "Installing prediction engine dependencies..."
    cd prediction-engine
    pip install -r requirements.txt
    cd ..

    # Install frontend dependencies
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..

    echo ""
    echo -e "${GREEN}All dependencies installed${NC}"
    echo ""

    # Start services in background
    echo "Starting services..."

    # Create logs directory
    mkdir -p logs

    # Start prediction engine
    echo "  - Starting prediction engine (port 8000)..."
    cd prediction-engine
    python3 main.py > ../logs/prediction-engine.log 2>&1 &
    ENGINE_PID=$!
    cd ..

    # Wait for engine to start
    sleep 3

    # Start backend
    echo "  - Starting backend server (port 5000)..."
    cd backend
    npm start > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..

    # Wait for backend to start
    sleep 3

    # Start frontend
    echo "  - Starting frontend (port 3000)..."
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo -e "${GREEN}All services started!${NC}"
    echo ""
    echo "Access the application at:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:5000"
    echo "  Engine:    http://localhost:8000"
    echo ""
    echo "View logs in the logs/ directory"
    echo ""
    echo "To stop all services, run: ./stop.sh"
    echo ""
    echo "Or press Ctrl+C to stop (services will continue in background)"

    # Save PIDs for stop script
    echo $ENGINE_PID > .engine.pid
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid

    # Wait indefinitely
    wait
fi
