/**
 * Predictions API Routes
 * Handles prediction creation, retrieval, and statistics
 */

import express from 'express';
import axios from 'axios';
import { Op } from 'sequelize';
import { models } from '../config/database.js';
import { createLogger } from '../config/logger.js';

const router = express.Router();
const { Prediction, Match } = models;
const logger = createLogger('predictions-api');

// Python prediction engine URL
const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000';

// POST /api/predictions/create - Create a new prediction
router.post('/create', async (req, res) => {
  try {
    const {
      home_team,
      away_team,
      league,
      match_date,
      home_odds,
      draw_odds,
      away_odds,
      opening_home_odds,
      opening_draw_odds,
      opening_away_odds,
      home_form,
      away_form,
      home_league_position,
      away_league_position,
      is_cup_match,
      home_matches_last_14_days,
      away_matches_last_14_days,
      weights,
    } = req.body;

    // Validate required fields
    if (!home_team || !away_team || !home_odds || !draw_odds || !away_odds) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds'],
      });
    }

    logger.info('Creating prediction', { home_team, away_team });

    // Call Python prediction engine (with extended timeout for scraper)
    const predictionResponse = await axios.post(
      `${PYTHON_ENGINE_URL}/api/predict`,
      {
        home_team,
        away_team,
        league,
        match_date: match_date || new Date().toISOString(),
        home_odds: parseFloat(home_odds),
        draw_odds: parseFloat(draw_odds),
        away_odds: parseFloat(away_odds),
        opening_home_odds: opening_home_odds ? parseFloat(opening_home_odds) : null,
        opening_draw_odds: opening_draw_odds ? parseFloat(opening_draw_odds) : null,
        opening_away_odds: opening_away_odds ? parseFloat(opening_away_odds) : null,
        // 不传form/position数据，让Python引擎使用爬虫获取
        // home_form,
        // away_form,
        // home_league_position,
        // away_league_position,
        is_cup_match,
        home_matches_last_14_days,
        away_matches_last_14_days,
        weights,
      },
      { timeout: 30000 }  // 增加到30秒，给爬虫足够时间
    );

    const predictionData = predictionResponse.data;

    // Save prediction to database
    const prediction = await Prediction.create({
      match_id: predictionData.match_id || `${home_team}-vs-${away_team}-${Date.now()}`,
      home_team: predictionData.home_team,
      away_team: predictionData.away_team,
      league: predictionData.league || league,
      match_date: predictionData.match_date,
      dimension_odds: predictionData.dimension_scores?.odds,
      dimension_injuries: predictionData.dimension_scores?.injuries,
      dimension_players: predictionData.dimension_scores?.players,
      dimension_tactics: predictionData.dimension_scores?.tactics,
      dimension_home_advantage: predictionData.dimension_scores?.home_advantage,
      dimension_referee: predictionData.dimension_scores?.referee,
      dimension_h2h: predictionData.dimension_scores?.h2h,
      dimension_motivation: predictionData.dimension_scores?.motivation,
      dimension_fitness: predictionData.dimension_scores?.fitness,
      home_win_probability: predictionData.home_win_probability,
      draw_probability: predictionData.draw_probability,
      away_win_probability: predictionData.away_win_probability,
      predicted_score: predictionData.predicted_score,
      predicted_winner: predictionData.predicted_winner,
      overall_confidence: predictionData.overall_confidence,
      key_insights: predictionData.key_insights,
      risk_factors: predictionData.risk_factors,
      recommended_bet: predictionData.recommended_bet,
      bet_confidence: predictionData.bet_confidence,
      custom_weights: weights,
    });

    logger.info('Prediction created', { prediction_id: prediction.id });

    res.status(201).json({
      success: true,
      prediction: {
        id: prediction.id,
        ...predictionData,
      },
    });
  } catch (error) {
    logger.error('Error creating prediction', {
      error: error.message,
      stack: error.stack,
    });

    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({
        error: 'Prediction engine unavailable',
        message: 'Unable to connect to Python prediction engine',
      });
    }

    res.status(500).json({
      error: 'Failed to create prediction',
      message: error.message,
    });
  }
});

// GET /api/predictions/:id - Get prediction by ID
router.get('/:id', async (req, res) => {
  try {
    const prediction = await Prediction.findByPk(req.params.id);

    if (!prediction) {
      return res.status(404).json({
        error: 'Prediction not found',
      });
    }

    res.json({
      success: true,
      prediction: prediction.toJSON(),
    });
  } catch (error) {
    logger.error('Error fetching prediction', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch prediction',
      message: error.message,
    });
  }
});

// GET /api/predictions/history - Get prediction history
router.get('/history/list', async (req, res) => {
  try {
    const {
      limit = 50,
      offset = 0,
      league,
      team,
      winner,
      is_correct,
      sort_by = 'created_at',
      sort_order = 'DESC',
    } = req.query;

    const where = {};

    if (league) {
      where.league = league;
    }

    if (team) {
      where[Op.or] = [
        { home_team: { [Op.like]: `%${team}%` } },
        { away_team: { [Op.like]: `%${team}%` } },
      ];
    }

    if (winner) {
      where.predicted_winner = winner;
    }

    if (is_correct !== undefined) {
      where.is_correct = is_correct === 'true';
    }

    const { count, rows } = await Prediction.findAndCountAll({
      where,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [[sort_by, sort_order.toUpperCase()]],
    });

    res.json({
      success: true,
      predictions: rows,
      total: count,
      limit: parseInt(limit),
      offset: parseInt(offset),
    });
  } catch (error) {
    logger.error('Error fetching prediction history', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch prediction history',
      message: error.message,
    });
  }
});

// GET /api/predictions/stats - Get prediction accuracy statistics
router.get('/stats/accuracy', async (req, res) => {
  try {
    const stats = await Prediction.findAll({
      where: {
        is_correct: { [Op.ne]: null },
      },
      attributes: [
        [sequelize.fn('COUNT', sequelize.col('id')), 'total'],
        [sequelize.fn('SUM', sequelize.literal("CASE WHEN is_correct = true THEN 1 ELSE 0 END")), 'correct'],
        [sequelize.fn('AVG', sequelize.col('overall_confidence')), 'avg_confidence'],
      ],
    });

    const total = parseInt(stats[0]?.dataValues?.total || 0);
    const correct = parseInt(stats[0]?.dataValues?.correct || 0);
    const accuracy = total > 0 ? (correct / total) * 100 : 0;
    const avgConfidence = parseFloat(stats[0]?.dataValues?.avg_confidence || 0);

    // By winner type
    const byWinner = await Prediction.findAll({
      where: {
        is_correct: { [Op.ne]: null },
      },
      attributes: [
        'predicted_winner',
        [sequelize.fn('COUNT', sequelize.col('id')), 'total'],
        [sequelize.fn('SUM', sequelize.literal("CASE WHEN is_correct = true THEN 1 ELSE 0 END")), 'correct'],
      ],
      group: ['predicted_winner'],
    });

    const byWinnerStats = byWinner.map((row) => ({
      winner: row.predicted_winner,
      total: parseInt(row.dataValues.total),
      correct: parseInt(row.dataValues.correct),
      accuracy: (row.dataValues.correct / row.dataValues.total) * 100,
    }));

    res.json({
      success: true,
      stats: {
        total_predictions: total,
        correct_predictions: correct,
        accuracy: Math.round(accuracy * 10) / 10,
        avg_confidence: Math.round(avgConfidence * 1000) / 1000,
        by_winner: byWinnerStats,
      },
    });
  } catch (error) {
    logger.error('Error fetching prediction stats', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch prediction stats',
      message: error.message,
    });
  }
});

// PUT /api/predictions/:id/result - Update actual result
router.put('/:id/result', async (req, res) => {
  try {
    const { actual_score, actual_winner } = req.body;

    const prediction = await Prediction.findByPk(req.params.id);

    if (!prediction) {
      return res.status(404).json({
        error: 'Prediction not found',
      });
    }

    const is_correct = prediction.predicted_winner === actual_winner;

    await prediction.update({
      actual_score,
      actual_winner,
      is_correct,
    });

    logger.info('Prediction result updated', {
      prediction_id: prediction.id,
      is_correct,
    });

    res.json({
      success: true,
      prediction: prediction.toJSON(),
    });
  } catch (error) {
    logger.error('Error updating prediction result', { error: error.message });
    res.status(500).json({
      error: 'Failed to update prediction result',
      message: error.message,
    });
  }
});

export default router;
