/**
 * Simplified Backend - Works on Railway without Python engine
 */

import express from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const THE_ODDS_API_KEY = process.env.THE_ODDS_API_KEY || '4091b3b46933315f5e88bf3cf953b3b4';

// Middleware
app.use(cors({
  origin: '*',
  credentials: true,
}));
app.use(express.json({ limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'football-predictor-backend-simple',
  });
});

// 支持的联赛列表
const LEAGUES = [
  { code: 'soccer_epl', name: '英超 Premier League', country: '英格兰' },
  { code: 'soccer_la_liga', name: '西甲 La Liga', country: '西班牙' },
  { code: 'soccer_bundesliga', name: '德甲 Bundesliga', country: '德国' },
  { code: 'soccer_serie_a', name: '意甲 Serie A', country: '意大利' },
  { code: 'soccer_ligue_1', name: '法甲 Ligue 1', country: '法国' },
];

// 获取联赛列表
app.get('/api/leagues', (req, res) => {
  res.json({ success: true, data: LEAGUES });
});

// 搜索比赛（演示数据）
app.get('/api/matches/search', async (req, res) => {
  try {
    const { league } = req.query;

    // 返回演示数据
    const demoMatches = [
      {
        id: '1',
        home_team: '阿森纳',
        away_team: '切尔西',
        league: 'soccer_epl',
        start_time: new Date(Date.now() + 86400000).toISOString(),
        home_win_odds: 2.50,
        draw_odds: 3.20,
        away_win_odds: 2.80,
      },
      {
        id: '2',
        home_team: '曼联',
        away_team: '利物浦',
        league: 'soccer_epl',
        start_time: new Date(Date.now() + 172800000).toISOString(),
        home_win_odds: 2.80,
        draw_odds: 3.10,
        away_win_odds: 2.60,
      },
    ];

    res.json({ success: true, matches: demoMatches });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 今日比赛
app.get('/api/matches/today', async (req, res) => {
  try {
    const demoMatches = [
      {
        id: '3',
        home_team: '皇家马德里',
        away_team: '巴塞罗那',
        league: 'soccer_la_liga',
        start_time: new Date().toISOString(),
        home_win_odds: 2.40,
        draw_odds: 3.30,
        away_win_odds: 2.90,
      },
    ];

    res.json({ success: true, matches: demoMatches });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 创建预测（演示模式）
app.post('/api/predictions/create', async (req, res) => {
  try {
    console.log('[Demo] Creating prediction for:', req.body);

    // 返回演示预测结果
    const demoPrediction = {
      match_id: req.body.match_id || 'demo',
      home_team: req.body.home_team || '主队',
      away_team: req.body.away_team || '客队',
      predicted_winner: 'home',
      confidence: 0.65,
      home_score: 2,
      away_score: 1,
      analysis: {
        odds_analysis: { score: 7.5, summary: '赔率市场看好主队' },
        injuries: { score: 6.0, summary: '无重大伤病' },
        player_form: { score: 7.0, summary: '球员状态良好' },
        tactics: { score: 6.5, summary: '战术对等' },
        home_advantage: { score: 7.0, summary: '主场优势明显' },
        referee: { score: 5.0, summary: '裁判因素中性' },
        h2h: { score: 6.0, summary: '历史战绩接近' },
        motivation: { score: 7.5, summary: '战意强烈' },
        fitness: { score: 6.5, summary: '体能状况良好' },
      },
      total_score: 6.5,
      recommendation: '建议投注：主队胜',
      created_at: new Date().toISOString(),
      disclaimer: '⚠️ 演示模式：这是模拟数据，实际预测需要完整的 Python 预测引擎。',
    };

    res.json({ success: true, prediction: demoPrediction });
  } catch (error) {
    console.error('[Demo] Error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// 快速预测（演示模式）
app.post('/api/predictions/quick', async (req, res) => {
  try {
    const demoPrediction = {
      match_id: 'demo-quick',
      home_team: req.body.home_team || '主队',
      away_team: req.body.away_team || '客队',
      predicted_winner: Math.random() > 0.5 ? 'home' : 'away',
      confidence: 0.55 + Math.random() * 0.2,
      recommendation: '演示预测',
      disclaimer: '⚠️ 演示模式',
    };

    res.json({ success: true, prediction: demoPrediction });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 九维分析（演示模式）
app.get('/api/analysis/nine-dimensions/:matchId', async (req, res) => {
  try {
    const demoAnalysis = {
      match_id: req.params.matchId,
      dimensions: [
        { name: '赔率市场', score: 7.5, weight: 0.15 },
        { name: '伤病情况', score: 6.0, weight: 0.10 },
        { name: '球员状态', score: 7.0, weight: 0.15 },
        { name: '战术分析', score: 6.5, weight: 0.10 },
        { name: '主场优势', score: 7.0, weight: 0.10 },
        { name: '裁判因素', score: 5.0, weight: 0.10 },
        { name: '历史交锋', score: 6.0, weight: 0.10 },
        { name: '战意分析', score: 7.5, weight: 0.10 },
        { name: '体能状况', score: 6.5, weight: 0.10 },
      ],
      total_score: 6.5,
      recommendation: '主队胜概率较高',
      disclaimer: '⚠️ 演示模式：这是模拟数据',
    };

    res.json({ success: true, analysis: demoAnalysis });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 预测历史（演示模式）
app.get('/api/predictions/history/list', (req, res) => {
  res.json({
    success: true,
    predictions: [
      {
        id: '1',
        home_team: '阿森纳',
        away_team: '切尔西',
        predicted_winner: 'home',
        actual_winner: 'home',
        confidence: 0.70,
        created_at: new Date().toISOString(),
      },
    ],
    disclaimer: '⚠️ 演示模式',
  });
});

// 准确率统计（演示模式）
app.get('/api/predictions/stats/accuracy', (req, res) => {
  res.json({
    success: true,
    stats: {
      total_predictions: 10,
      correct: 7,
      accuracy: 0.70,
      disclaimer: '⚠️ 演示模式',
    },
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`=`.repeat(60));
  console.log(`  Football Predictor Backend - SIMPLIFIED VERSION`);
  console.log(`=`.repeat(60));
  console.log(`  Server running on port ${PORT}`);
  console.log(`  Demo mode: Python engine not required`);
  console.log(`  http://localhost:${PORT}`);
  console.log(`=`.repeat(60));
});
