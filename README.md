# Football Predictor - Nine Dimensions

> Advanced AI-powered football match predictions using nine-dimensional holistic analysis

A full-stack web application that implements a sophisticated football prediction model based on odds market analysis, team form, injuries, tactical matchups, and five other critical dimensions.

## 🌟 Features

- **Nine-Dimensional Prediction Model**
  - Odds market analysis and trends
  - Injury and suspension impact
  - Player form and matchups
  - Manager tactical compatibility
  - Home advantage calculation
  - Referee factors
  - Head-to-head history
  - Match motivation assessment
  - Fitness and fatigue analysis

- **Real-Time Data Integration**
  - The Odds API for live odds data
  - API-Football for comprehensive match data
  - Intelligent caching to optimize API usage

- **Interactive Dashboard**
  - Today's matches overview
  - Create custom predictions
  - Nine-dimensional radar chart visualization
  - Prediction history and accuracy tracking

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ (Vite + shadcn/ui)
│   Port: 3000    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Node.js Backend│ (Express + Sequelize)
│   Port: 5000    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Python Engine   │ (Flask + NumPy)
│   Port: 8000    │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- (Optional) Docker & Docker Compose

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd football-predictor-app

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# Start all services
./start.sh
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

### Option 2: Local Development

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install Python dependencies
cd prediction-engine
pip install -r requirements.txt
cd ..

# 3. Install backend dependencies
cd backend
npm install
cd ..

# 4. Install frontend dependencies
cd frontend
npm install
cd ..

# 5. Start services (in separate terminals)
# Terminal 1: Prediction Engine
cd prediction-engine
python main.py

# Terminal 2: Backend
cd backend
npm start

# Terminal 3: Frontend
cd frontend
npm run dev
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` file with your API keys:

```bash
# The Odds API (Required)
THE_ODDS_API_KEY=your_key_here
# Get free key at: https://api.the-odds-api.com/

# API-Football (Optional but recommended)
API_FOOTBALL_KEY=your_key_here
# Get free key at: https://api-football.com/register
# Free tier: 100 requests/month

# Server Ports
PORT=5000          # Backend
PYTHON_ENGINE_PORT=8000  # Prediction Engine

# Database (SQLite for development)
SQLITE_PATH=./database/football_predictor.sqlite
```

### API Key Setup

#### The Odds API (Required)

1. Visit https://api.the-odds-api.com/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add to `.env`: `THE_ODDS_API_KEY=your_key`

#### API-Football (Optional)

1. Visit https://api-football.com/register
2. Create a free account (100 requests/month)
3. Get your API key
4. Add to `.env`: `API_FOOTBALL_KEY=your_key`

## 📖 Usage

### Creating a Prediction

1. Navigate to http://localhost:3000
2. Click "Create Prediction"
3. Enter match details:
   - Home/Away teams (required)
   - Current odds (required)
   - Optional: Form, league position, etc.
4. Click "Generate Prediction"
5. View nine-dimensional analysis and prediction

### Viewing Analysis

- **Radar Chart**: Visual breakdown of all nine dimensions
- **Dimension Scores**: Detailed analysis per dimension
- **Key Insights**: AI-generated insights and risk factors
- **Bet Recommendations**: Value bet suggestions with confidence

### Tracking Accuracy

- Navigate to "History" page
- View all past predictions
- Track accuracy over time
- Update results as matches finish

## 🔮 Nine-Dimensional Model

The prediction model analyzes nine key dimensions:

1. **Odds Market** - Market sentiment and odds movements
2. **Injuries** - Impact of injured/suspended players
3. **Player Form** - Recent performance and matchups
4. **Tactics** - Manager tactical compatibility
5. **Home Advantage** - Historical home/away records
6. **Referee** - Referee style and tendencies
7. **Head-to-Head** - Historical psychological advantage
8. **Motivation** - Match importance and context
9. **Fitness** - Schedule density and fatigue levels

Each dimension is scored 0-1, weighted, and combined to generate win probabilities and predicted scores.

## 🗂️ Project Structure

```
football-predictor-app/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/        # Page components
│   │   └── lib/          # Utilities
│   └── package.json
├── backend/              # Node.js backend
│   ├── src/
│   │   ├── api/         # API routes
│   │   ├── models/      # Database models
│   │   └── config/      # Configuration
│   └── package.json
├── prediction-engine/    # Python prediction engine
│   ├── models/          # Nine-dimension model
│   ├── services/        # API integration
│   └── requirements.txt
├── database/            # SQLite database
├── docker-compose.yml   # Docker configuration
├── .env.example         # Environment template
├── start.sh            # One-command startup
└── README.md
```

## 🔧 API Endpoints

### Backend (Port 5000)

- `POST /api/predictions/create` - Create prediction
- `GET /api/predictions/:id` - Get prediction
- `GET /api/predictions/history/list` - Get history
- `GET /api/predictions/stats/accuracy` - Get accuracy stats
- `GET /api/matches/today` - Get today's matches
- `POST /api/matches/sync` - Sync from The Odds API
- `GET /api/analysis/nine-dimensions/:matchId` - Get analysis
- `GET /api/sync/status` - Service status

### Prediction Engine (Port 8000)

- `POST /api/predict` - Generate prediction
- `POST /api/predict/quick` - Quick prediction
- `GET /health` - Health check

## 🧪 Testing

```bash
# Test Python prediction engine
cd prediction-engine
python models/nine_dimensions.py

# Test backend API
curl http://localhost:5000/health

# Test frontend
npm run test
```

## 📈 Production Deployment

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Set `NODE_ENV=production`
3. Configure CORS for your domain
4. Use a process manager (PM2)
5. Set up reverse proxy (Nginx)
6. Enable HTTPS
7. Configure rate limiting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## ⚠️ Disclaimer

This application is for informational and educational purposes only. Gambling involves risk. Please gamble responsibly and only bet what you can afford to lose. Past predictions do not guarantee future results.

## 🙏 Acknowledgments

- The Odds API for providing odds data
- API-Football for comprehensive football data
- shadcn/ui for beautiful UI components
- Recharts for data visualization
