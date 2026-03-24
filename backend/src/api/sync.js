/**
 * Sync API Routes
 * Handles data synchronization from external APIs
 */

import express from 'express';
import axios from 'axios';
import { createLogger } from '../config/logger.js';

const router = express.Router();
const logger = createLogger('sync-api');

// GET /api/sync/status - Get sync status
router.get('/status', async (req, res) => {
  try {
    // Check Python engine status
    const pythonEngineUrl = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000';

    let engineStatus = 'unknown';
    try {
      const response = await axios.get(`${pythonEngineUrl}/health`, { timeout: 3000 });
      engineStatus = response.data.status === 'healthy' ? 'healthy' : 'unhealthy';
    } catch (error) {
      engineStatus = 'unreachable';
    }

    res.json({
      success: true,
      services: {
        python_engine: engineStatus,
        the_odds_api: process.env.THE_ODDS_API_KEY ? 'configured' : 'not_configured',
        api_football: process.env.API_FOOTBALL_KEY ? 'configured' : 'not_configured',
      },
    });
  } catch (error) {
    logger.error('Error checking sync status', { error: error.message });
    res.status(500).json({
      error: 'Failed to check sync status',
      message: error.message,
    });
  }
});

// POST /api/sync/cache/clear - Clear Python engine cache
router.post('/cache/clear', async (req, res) => {
  try {
    const { category } = req.body;
    const pythonEngineUrl = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000';

    const response = await axios.post(
      `${pythonEngineUrl}/api/cache/clear`,
      { category },
      { timeout: 5000 }
    );

    res.json({
      success: true,
      ...response.data,
    });
  } catch (error) {
    logger.error('Error clearing cache', { error: error.message });
    res.status(500).json({
      error: 'Failed to clear cache',
      message: error.message,
    });
  }
});

// GET /api/sync/cache/stats - Get cache statistics
router.get('/cache/stats', async (req, res) => {
  try {
    const pythonEngineUrl = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000';

    const response = await axios.get(`${pythonEngineUrl}/api/cache/stats`, {
      timeout: 5000,
    });

    res.json({
      success: true,
      ...response.data,
    });
  } catch (error) {
    logger.error('Error fetching cache stats', { error: error.message });
    res.status(500).json({
      error: 'Failed to fetch cache stats',
      message: error.message,
    });
  }
});

export default router;
