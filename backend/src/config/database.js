/**
 * Database Configuration
 * Sequelize ORM setup with SQLite (development) and PostgreSQL (production)
 */

import dotenv from 'dotenv';

dotenv.config();

// Import Sequelize dynamically (better-sqlite3 needs to be required)
let Sequelize;
try {
  Sequelize = require('sequelize');
} catch (e) {
  // Fallback to ES import
  const sequelizeModule = await import('sequelize');
  Sequelize = sequelizeModule.default;
}

// Determine database dialect
const isProduction = process.env.NODE_ENV === 'production';
const dialect = process.env.DB_DIALECT || (isProduction ? 'postgres' : 'sqlite');

let sequelize;

// SQLite configuration (development)
if (dialect === 'sqlite') {
  const sqlitePath = process.env.SQLITE_PATH || './database/football_predictor.sqlite';
  const { Sequelize } = require('sequelize');

  // Use better-sqlite3 dialect
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: sqlitePath,
    dialectModule: require('better-sqlite3'),
    logging: process.env.DB_LOGGING === 'true' ? console.log : false,
    define: {
      timestamps: true,
      underscored: true,
      createdAt: 'created_at',
      updatedAt: 'updated_at',
    },
  });
}
// PostgreSQL configuration (production)
else if (dialect === 'postgres') {
  sequelize = new Sequelize({
    dialect: 'postgres',
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'football_predictor',
    username: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || 'postgres',
    logging: process.env.DB_LOGGING === 'true' ? console.log : false,
    define: {
      timestamps: true,
      underscored: true,
      createdAt: 'created_at',
      updatedAt: 'updated_at',
    },
    pool: {
      max: 20,
      min: 5,
      acquire: 60000,
      idle: 10000,
    },
  });
} else {
  throw new Error(`Unsupported database dialect: ${dialect}`);
}

// Import models
import Match from '../models/Match.js';
import Prediction from '../models/Prediction.js';
import Team from '../models/Team.js';
import Player from '../models/Player.js';
import Referee from '../models/Referee.js';
import OddsHistory from '../models/OddsHistory.js';

// Initialize models
const models = {
  Match: Match(sequelize),
  Prediction: Prediction(sequelize),
  Team: Team(sequelize),
  Player: Player(sequelize),
  Referee: Referee(sequelize),
  OddsHistory: OddsHistory(sequelize),
};

// Setup associations
Object.values(models).forEach((model) => {
  if (model.associate) {
    model.associate(models);
  }
});

// Test database connection
export async function testConnection() {
  try {
    await sequelize.authenticate();
    console.log('Database connection established successfully');
  } catch (error) {
    console.error('Unable to connect to database:', error);
    throw error;
  }
}

// Initialize database tables
export async function initDB(force = false) {
  try {
    await sequelize.sync({ force, alter: !force });
    console.log('Database tables initialized');
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  }
}

// Export sequelize and models
export { sequelize, models };

export default sequelize;
