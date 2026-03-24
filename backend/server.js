/**
 * Backend Server - Fetch real odds from The Odds API
 */

import express from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = 5000;
const THE_ODDS_API_KEY = '4091b3b46933315f5e88bf3cf953b3b4';

// Middleware
app.use(cors({
  origin: '*', // 允许所有来源（便于分享）
  credentials: true,
}));
app.use(express.json({ limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'football-predictor-backend',
  });
});

// 支持的联赛列表
const LEAGUES = [
  // 欧洲五大联赛
  { code: 'soccer_epl', name: '英超 Premier League', country: '英格兰' },
  { code: 'soccer_la_liga', name: '西甲 La Liga', country: '西班牙' },
  { code: 'soccer_bundesliga', name: '德甲 Bundesliga', country: '德国' },
  { code: 'soccer_serie_a', name: '意甲 Serie A', country: '意大利' },
  { code: 'soccer_ligue_1', name: '法甲 Ligue 1', country: '法国' },

  // 欧洲其他联赛
  { code: 'soccer_eredivisie', name: '荷甲 Eredivisie', country: '荷兰' },
  { code: 'soccer_primeira_liga', name: '葡超 Primeira Liga', country: '葡萄牙' },
  { code: 'soccer_championship', name: '英冠 Championship', country: '英格兰' },
  { code: 'soccer_bundesliga2', name: '德乙 2. Bundesliga', country: '德国' },
  { code: 'soccer_serie_b', name: '意乙 Serie B', country: '意大利' },
  { code: 'soccer_ligue_2', name: '法乙 Ligue 2', country: '法国' },

  // 欧洲杯赛
  { code: 'soccer_champions_league', name: '欧冠 UEFA Champions League', country: '欧洲' },
  { code: 'soccer_europa_league', name: '欧联 UEFA Europa League', country: '欧洲' },
  { code: 'soccer_uefa_nations_league', name: '欧洲国家联赛 Nations League', country: '欧洲' },

  // 亚洲联赛
  { code: 'soccer_jleague_1', name: '日职联 J1 League', country: '日本' },
  { code: 'soccer_jleague_2', name: '日乙 J2 League', country: '日本' },
  { code: 'soccer_k_league_1', name: 'K联赛1 K League 1', country: '韩国' },
  { code: 'soccer_k_league_2', name: 'K联赛2 K League 2', country: '韩国' },
  { code: 'soccer_csl', name: '中超 Chinese Super League', country: '中国' },
  { code: 'soccer_saudi_league', name: '沙特职业联赛 Saudi Pro League', country: '沙特' },
  { code: 'soccer_a_league', name: '澳超 A-League', country: '澳大利亚' },

  // 美洲联赛
  { code: 'soccer_mls', name: '美职联 MLS', country: '美国' },
  { code: 'soccer_brazil_serie_a', name: '巴甲 Brasileirão', country: '巴西' },
  { code: 'soccer_liga_mx', name: '墨联 Liga MX', country: '墨西哥' },
  { code: 'soccer_libertadores', name: '南美解放者杯', country: '南美' },

  // 其他热门联赛
  { code: 'soccer_super_lig', name: '土超 Süper Lig', country: '土耳其' },
  { code: 'soccer_championship', name: '俄超 Russian Premier', country: '俄罗斯' },
  { code: 'soccer_scottish_premiership', name: '苏超 Scottish Premiership', country: '苏格兰' },
  { code: 'soccer_liga_portugal', name: '葡超 Liga Portugal', country: '葡萄牙' },
];

// 获取支持的联赛列表
app.get('/api/leagues', (req, res) => {
  res.json({
    success: true,
    leagues: LEAGUES,
  });
});

// 根据联赛、日期、球队搜索比赛
app.get('/api/matches/search', async (req, res) => {
  // 在函数开始时就解构参数，这样 catch 块也能访问到
  const { league, date, home_team, away_team } = req.query;

  try {
    console.log('[Backend] Searching matches:', { league, date, home_team, away_team });

    // 构建API请求
    const sport = league || 'soccer_epl';
    let apiUrl = `https://api.the-odds-api.com/v4/sports/${sport}/odds`;

    const params = {
      apiKey: THE_ODDS_API_KEY,
      regions: 'eu',
      markets: 'h2h',
      dateFormat: 'iso',
    };

    // 如果指定了日期，添加时间范围
    if (date) {
      const startDate = new Date(date);
      const endDate = new Date(date);
      endDate.setDate(endDate.getDate() + 1);

      params.commenceTimeFrom = startDate.toISOString();
      params.commenceTimeTo = endDate.toISOString();
    }

    const response = await axios.get(apiUrl, { params, timeout: 10000 });

    let matches = response.data.map(match => {
      const bookmakers = match.bookmakers || [];
      const mainBookmaker = bookmakers[0];

      if (mainBookmaker) {
        const h2hMarket = mainBookmaker.markets?.find(m => m.key === 'h2h');
        if (h2hMarket && h2hMarket.outcomes && h2hMarket.outcomes.length >= 3) {
          const homeOutcome = h2hMarket.outcomes.find(o => o.name === match.home_team);
          const drawOutcome = h2hMarket.outcomes.find(o => o.name === 'Draw');
          const awayOutcome = h2hMarket.outcomes.find(o => o.name === match.away_team);

          return {
            id: match.id,
            home_team: match.home_team,
            away_team: match.away_team,
            league: LEAGUES.find(l => l.code === sport)?.name || match.sport_title,
            league_code: sport,
            match_date: match.commence_time,
            status: 'scheduled',
            home_odds: homeOutcome?.price || null,
            draw_odds: drawOutcome?.price || null,
            away_odds: awayOutcome?.price || null,
          };
        }
      }
      return null;
    }).filter(m => m !== null);

    // 按球队筛选
    if (home_team) {
      matches = matches.filter(m =>
        m.home_team.toLowerCase().includes(home_team.toLowerCase())
      );
    }
    if (away_team) {
      matches = matches.filter(m =>
        m.away_team.toLowerCase().includes(away_team.toLowerCase())
      );
    }

    console.log(`[Backend] Found ${matches.length} matches`);

    res.json({
      success: true,
      matches: matches,
      filters: { league, date, home_team, away_team },
    });
  } catch (error) {
    console.error('[Backend] Error searching matches:', error.message);

    // 检查错误类型
    if (error.response?.status === 404) {
      // 该联赛暂无数据
      const leagueName = LEAGUES.find(l => l.code === league)?.name || league;
      return res.json({
        success: true,
        matches: [],
        error: `该日期的${leagueName}暂无比赛数据`,
        filters: { league, date },
      });
    } else if (error.response?.status === 422) {
      // 请求参数错误
      return res.json({
        success: true,
        matches: [],
        error: '搜索参数无效，请检查日期格式',
        filters: { league, date },
      });
    } else {
      // 其他错误
      return res.json({
        success: true,
        matches: [],
        error: '无法获取比赛数据，请稍后重试',
        filters: { league, date },
      });
    }
  }
});

// Fetch real matches from The Odds API
app.get('/api/matches/today', async (req, res) => {
  try {
    console.log('[Backend] Fetching matches from The Odds API...');

    const response = await axios.get(
      `https://api.the-odds-api.com/v4/sports/soccer/odds`,
      {
        params: {
          apiKey: THE_ODDS_API_KEY,
          regions: 'eu',
          markets: 'h2h',
          dateFormat: 'iso',
        },
        timeout: 10000,
      }
    );

    const matches = response.data.slice(0, 20).map(match => {
      const bookmakers = match.bookmakers || [];
      const mainBookmaker = bookmakers[0];

      if (mainBookmaker) {
        const h2hMarket = mainBookmaker.markets?.find(m => m.key === 'h2h');
        if (h2hMarket && h2hMarket.outcomes && h2hMarket.outcomes.length >= 3) {
          const homeOutcome = h2hMarket.outcomes.find(o => o.name === match.home_team);
          const drawOutcome = h2hMarket.outcomes.find(o => o.name === 'Draw');
          const awayOutcome = h2hMarket.outcomes.find(o => o.name === match.away_team);

          return {
            id: match.id,
            home_team: match.home_team,
            away_team: match.away_team,
            league: match.sport_title,
            match_date: match.commence_time,
            status: 'scheduled',
            home_odds: homeOutcome?.price || null,
            draw_odds: drawOutcome?.price || null,
            away_odds: awayOutcome?.price || null,
          };
        }
      }
      return null;
    }).filter(m => m !== null);

    console.log(`[Backend] Found ${matches.length} matches with odds`);

    res.json({
      success: true,
      matches: matches,
      date: new Date().toISOString().split('T')[0],
    });
  } catch (error) {
    console.error('[Backend] Error fetching matches:', error.message);

    // Return fallback data if API fails
    res.json({
      success: true,
      matches: [
        {
          id: '1',
          home_team: '阿森纳',
          away_team: '切尔西',
          league: 'Premier League',
          match_date: new Date().toISOString(),
          home_odds: 2.10,
          draw_odds: 3.40,
          away_odds: 3.60,
        },
        {
          id: '2',
          home_team: '曼城',
          away_team: '利物浦',
          league: 'Premier League',
          match_date: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
          home_odds: 1.85,
          draw_odds: 3.60,
          away_odds: 4.20,
        },
        {
          id: '3',
          home_team: '皇家马德里',
          away_team: '巴塞罗那',
          league: 'La Liga',
          match_date: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(),
          home_odds: 2.50,
          draw_odds: 3.20,
          away_odds: 2.80,
        },
        {
          id: '4',
          home_team: '拜仁慕尼黑',
          away_team: '多特蒙德',
          league: 'Bundesliga',
          match_date: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
          home_odds: 1.65,
          draw_odds: 4.00,
          away_odds: 5.50,
        },
      ],
      date: new Date().toISOString().split('T')[0],
      fallback: true,
    });
  }
});

// Proxy prediction requests to Python engine
app.post('/api/predictions/create', async (req, res) => {
  try {
    console.log(`[Backend] Creating prediction: ${req.body.home_team} vs ${req.body.away_team}`);

    const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:8002';
    const TIMEOUT = parseInt(process.env.PREDICTION_TIMEOUT || '60000'); // 增加到 60 秒

    const response = await axios.post(`${PYTHON_ENGINE_URL}/api/predict`, req.body, {
      headers: { 'Content-Type': 'application/json' },
      timeout: TIMEOUT,
    });

    res.json({ success: true, prediction: response.data });
  } catch (error) {
    console.error('[Backend] Error:', error.message);
    if (error.code === 'ECONNABORTED') {
      res.status(408).json({
        error: { error: '预测超时，请稍后重试。完整预测需要 20-40 秒。' }
      });
    } else {
      res.status(error.response?.status || 500).json({
        error: error.response?.data || { error: 'Prediction failed' },
      });
    }
  }
});

// Quick prediction endpoint
app.post('/api/predictions/quick', async (req, res) => {
  try {
    const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:8002';
    const TIMEOUT = parseInt(process.env.PREDICTION_TIMEOUT || '60000'); // 增加到 60 秒

    const response = await axios.post(`${PYTHON_ENGINE_URL}/api/predict/quick`, req.body, {
      headers: { 'Content-Type': 'application/json' },
      timeout: TIMEOUT,
    });
    res.json({ success: true, prediction: response.data });
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      res.status(408).json({
        error: { error: '预测超时，请稍后重试。' }
      });
    } else {
      res.status(error.response?.status || 500).json({
        error: error.response?.data || { error: 'Prediction failed' },
      });
    }
  }
});

// History endpoint
app.get('/api/predictions/history/list', (req, res) => {
  res.json({
    success: true,
    predictions: [],
    total: 0,
  });
});

// Stats endpoint
app.get('/api/predictions/stats/accuracy', (req, res) => {
  res.json({
    success: true,
    stats: {
      total_predictions: 0,
      correct_predictions: 0,
      accuracy: 0,
      avg_confidence: 0,
    },
  });
});

// Analysis endpoint
app.get('/api/analysis/nine-dimensions/:matchId', async (req, res) => {
  try {
    const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:8002';
    const TIMEOUT = parseInt(process.env.PREDICTION_TIMEOUT || '30000');

    const response = await axios.get(`${PYTHON_ENGINE_URL}/api/analysis/nine-dimensions/${req.params.matchId}`, {
      timeout: TIMEOUT,
    });
    res.json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json({
      error: 'Failed to fetch analysis',
    });
  }
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`,
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({
    error: 'Internal Server Error',
    message: err.message,
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`=`.repeat(60));
  console.log(`  Football Predictor Backend`);
  console.log(`=`.repeat(60));
  console.log(`  Server running on port ${PORT}`);
  console.log(`  Fetching real odds from The Odds API`);
  console.log(`  http://localhost:${PORT}`);
  console.log(`=`.repeat(60));
});
