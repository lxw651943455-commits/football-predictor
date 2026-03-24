/**
 * Analysis API Routes
 * Provides nine-dimensional analysis and insights
 */

import express from 'express';
import { Op } from 'sequelize';
import axios from 'axios';
import { models } from '../config/database.js';
import { createLogger } from '../config/logger.js';

const router = express.Router();
const { Prediction, Match } = models;
const logger = createLogger('analysis-api');

// Python prediction engine URL
const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000';

// GET /api/analysis/nine-dimensions/:matchId - Get nine-dimensional analysis
router.get('/nine-dimensions/:matchId', async (req, res) => {
  try {
    const { matchId } = req.params;

    // Find prediction
    const prediction = await Prediction.findOne({
      where: { match_id: matchId },
    });

    if (!prediction) {
      return res.status(404).json({
        error: 'Prediction not found for this match',
      });
    }

    // Return dimension scores
    const dimensionScores = {
      odds: prediction.dimension_odds,
      injuries: prediction.dimension_injuries,
      players: prediction.dimension_players,
      tactics: prediction.dimension_tactics,
      home_advantage: prediction.dimension_home_advantage,
      referee: prediction.dimension_referee,
      h2h: prediction.dimension_h2h,
      motivation: prediction.dimension_motivation,
      fitness: prediction.dimension_fitness,
    };

    res.json({
      success: true,
      match_id: matchId,
      home_team: prediction.home_team,
      away_team: prediction.away_team,
      dimension_scores: dimensionScores,
      predicted_winner: prediction.predicted_winner,
      confidence: prediction.overall_confidence,
      insights: prediction.key_insights,
      risks: prediction.risk_factors,
    });
  } catch (error) {
    logger.error('Error fetching nine-dimension analysis', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch analysis',
      message: error.message,
    });
  }
});

// GET /api/analysis/trends - Get prediction trends
router.get('/trends', async (req, res) => {
  try {
    const { days = 30, dimension } = req.query;

    const startDate = new Date();
    startDate.setDate(startDate.getDate() - parseInt(days));

    const predictions = await Prediction.findAll({
      where: {
        created_at: {
          [Op.gte]: startDate,
        },
      },
      order: [['created_at', 'ASC']],
    });

    // Calculate trends
    const trends = {
      total_predictions: predictions.length,
      avg_confidence: 0,
      dimension_averages: {},
      winner_distribution: {
        home: 0,
        draw: 0,
        away: 0,
      },
      daily_predictions: [],
    };

    if (predictions.length > 0) {
      // Average confidence
      trends.avg_confidence =
        predictions.reduce((sum, p) => sum + p.overall_confidence, 0) / predictions.length;

      // Dimension averages
      const dimensions = [
        'odds',
        'injuries',
        'players',
        'tactics',
        'home_advantage',
        'referee',
        'h2h',
        'motivation',
        'fitness',
      ];

      dimensions.forEach((dim) => {
        const values = predictions.map((p) => p[`dimension_${dim}`]).filter((v) => v !== null);
        if (values.length > 0) {
          trends.dimension_averages[dim] = values.reduce((sum, v) => sum + v, 0) / values.length;
        }
      });

      // Winner distribution
      predictions.forEach((p) => {
        trends.winner_distribution[p.predicted_winner]++;
      });

      // Daily predictions
      const byDay = {};
      predictions.forEach((p) => {
        const day = p.created_at.toISOString().split('T')[0];
        byDay[day] = (byDay[day] || 0) + 1;
      });

      trends.daily_predictions = Object.entries(byDay).map(([day, count]) => ({
        date: day,
        count,
      }));
    }

    res.json({
      success: true,
      trends,
      period_days: parseInt(days),
    });
  } catch (error) {
    logger.error('Error fetching trends', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch trends',
      message: error.message,
    });
  }
});

// GET /api/analysis/top-predictions - Get top confidence predictions
router.get('/top-predictions', async (req, res) => {
  try {
    const { limit = 10, min_confidence = 0.6 } = req.query;

    const predictions = await Prediction.findAll({
      where: {
        overall_confidence: {
          [Op.gte]: parseFloat(min_confidence),
        },
        match_date: {
          [Op.gte]: new Date(),
        },
      },
      order: [['overall_confidence', 'DESC']],
      limit: parseInt(limit),
    });

    res.json({
      success: true,
      predictions,
      count: predictions.length,
    });
  } catch (error) {
    logger.error('Error fetching top predictions', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch top predictions',
      message: error.message,
    });
  }
});

// POST /api/analysis/batch-predict - Batch predict multiple matches
router.post('/batch-predict', async (req, res) => {
  try {
    const { matches } = req.body;

    if (!matches || !Array.isArray(matches) || matches.length === 0) {
      return res.status(400).json({
        error: 'Invalid request',
        message: 'matches array is required',
      });
    }

    if (matches.length > 20) {
      return res.status(400).json({
        error: 'Too many matches',
        message: 'Maximum 20 matches per batch',
      });
    }

    logger.info('Batch prediction', { count: matches.length });

    const predictions = [];

    for (const match of matches) {
      try {
        const response = await axios.post(
          `${PYTHON_ENGINE_URL}/api/predict/quick`,
          match,
          { timeout: 5000 }
        );
        predictions.push(response.data);
      } catch (error) {
        logger.error('Failed to predict match', { match, error: error.message });
        predictions.push({
          home_team: match.home_team,
          away_team: match.away_team,
          error: error.message,
        });
      }
    }

    res.json({
      success: true,
      predictions,
      total: predictions.length,
    });
  } catch (error) {
    logger.error('Error in batch prediction', { error: error.message });
    res.status(500).json({
      error: 'Failed to complete batch prediction',
      message: error.message,
    });
  }
});

export default router;
