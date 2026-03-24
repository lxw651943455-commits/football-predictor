/**
 * Matches API Routes
 * Handles match data and scheduling
 */

import express from 'express';
import { Op } from 'sequelize';
import axios from 'axios';
import { models } from '../config/database.js';
import { createLogger } from '../config/logger.js';

const router = express.Router();
const { Match, Prediction } = models;
const logger = createLogger('matches-api');

// GET /api/matches/today - Get today's matches
router.get('/today', async (req, res) => {
  try {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const matches = await Match.findAll({
      where: {
        match_date: {
          [Op.gte]: today,
          [Op.lt]: tomorrow,
        },
        status: 'scheduled',
      },
      order: [['match_date', 'ASC']],
      limit: 100,
    });

    res.json({
      success: true,
      matches,
      date: today.toISOString().split('T')[0],
    });
  } catch (error) {
    logger.error('Error fetching today\'s matches', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch matches',
      message: error.message,
    });
  }
});

// GET /api/matches/:id - Get match by ID
router.get('/:id', async (req, res) => {
  try {
    const match = await Match.findByPk(req.params.id, {
      include: [{ model: Prediction, as: 'prediction' }],
    });

    if (!match) {
      return res.status(404).json({
        error: 'Match not found',
      });
    }

    res.json({
      success: true,
      match: match.toJSON(),
    });
  } catch (error) {
    logger.error('Error fetching match', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch match',
      message: error.message,
    });
  }
});

// GET /api/matches/league/:league - Get matches by league
router.get('/league/:league', async (req, res) => {
  try {
    const { league } = req.params;
    const { status, limit = 50, offset = 0 } = req.query;

    const where = { league };
    if (status) {
      where.status = status;
    }

    const { count, rows } = await Match.findAndCountAll({
      where,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['match_date', 'DESC']],
    });

    res.json({
      success: true,
      matches: rows,
      total: count,
      league,
    });
  } catch (error) {
    logger.error('Error fetching league matches', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch matches',
      message: error.message,
    });
  }
});

// POST /api/matches/sync - Sync matches from The Odds API
router.post('/sync', async (req, res) => {
  try {
    const { sport = 'soccer', regions = 'eu', markets = 'h2h' } = req.body;

    logger.info('Syncing matches from The Odds API');

    const odds_api_key = process.env.THE_ODDS_API_KEY;
    if (!odds_api_key) {
      return res.status(500).json({
        error: 'The Odds API key not configured',
      });
    }

    const url = `https://api.the-odds-api.com/v4/sports/${sport}/odds`;
    const response = await axios.get(url, {
      params: {
        apiKey: odds_api_key,
        regions,
        markets,
        dateFormat: 'iso',
      },
    });

    const matches = response.data;

    // Process and store matches
    const processedMatches = [];
    for (const match of matches) {
      const existingMatch = await Match.findOne({
        where: { odds_api_match_id: match.id },
      });

      const bookmakers = match.bookmakers || [];
      const mainBookmaker = bookmakers[0];

      if (mainBookmaker) {
        const h2hMarkets = mainBookmaker.markets.find((m) => m.key === 'h2h');
        if (h2hMarkets && h2hMarkets.outcomes.length >= 3) {
          const homeOutcome = h2hMarkets.outcomes.find((o) => o.name === match.home_team);
          const drawOutcome = h2hMarkets.outcomes.find((o) => o.name === 'Draw');
          const awayOutcome = h2hMarkets.outcomes.find((o) => o.name === match.away_team);

          const matchData = {
            odds_api_match_id: match.id,
            home_team: match.home_team,
            away_team: match.away_team,
            league: match.sport_title,
            match_date: new Date(match.commence_time),
            status: 'scheduled',
            home_odds: homeOutcome?.price,
            draw_odds: drawOutcome?.price,
            away_odds: awayOutcome?.price,
          };

          if (existingMatch) {
            await existingMatch.update(matchData);
            processedMatches.push({ ...existingMatch.toJSON(), isNew: false });
          } else {
            const newMatch = await Match.create(matchData);
            processedMatches.push({ ...newMatch.toJSON(), isNew: true });
          }
        }
      }
    }

    logger.info('Matches synced', { count: processedMatches.length });

    res.json({
      success: true,
      matches: processedMatches,
      synced: processedMatches.length,
      new: processedMatches.filter((m) => m.isNew).length,
    });
  } catch (error) {
    logger.error('Error syncing matches', { error: error.message, stack: error.stack });
    res.status(500).json({
      error: 'Failed to sync matches',
      message: error.message,
    });
  }
});

export default router;
