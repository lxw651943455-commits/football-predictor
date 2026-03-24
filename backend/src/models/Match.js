/**
 * Match Model
 * Stores match information and results
 */

import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const Match = sequelize.define('Match', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },

    // External IDs
    odds_api_match_id: {
      type: DataTypes.STRING,
      allowNull: true,
      unique: true,
    },

    api_football_fixture_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    // Match details
    home_team: {
      type: DataTypes.STRING,
      allowNull: false,
      index: true,
    },

    away_team: {
      type: DataTypes.STRING,
      allowNull: false,
      index: true,
    },

    league: {
      type: DataTypes.STRING,
      allowNull: false,
      index: true,
    },

    league_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    match_date: {
      type: DataTypes.DATE,
      allowNull: false,
      index: true,
    },

    status: {
      type: DataTypes.ENUM('scheduled', 'live', 'finished', 'postponed', 'cancelled'),
      defaultValue: 'scheduled',
      index: true,
    },

    // Odds
    home_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    draw_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    away_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    opening_home_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    opening_draw_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    opening_away_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    asian_handicap: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    over_under: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    // Actual result
    home_score: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    away_score: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    winner: {
      type: DataTypes.ENUM('home', 'draw', 'away', null),
      allowNull: true,
    },

    // Reference to prediction
    prediction_id: {
      type: DataTypes.UUID,
      allowNull: true,
      references: {
        model: 'predictions',
        key: 'id',
      },
    },

    // Metadata
    home_team_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    away_team_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    referee_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    venue: {
      type: DataTypes.STRING,
      allowNull: true,
    },

  }, {
    tableName: 'matches',
    indexes: [
      { fields: ['match_date'] },
      { fields: ['league'] },
      { fields: ['status'] },
      { fields: ['home_team', 'away_team'] },
      { fields: ['prediction_id'] },
    ],
  });

  Match.associate = (models) => {
    Match.belongsTo(models.Prediction, {
      foreignKey: 'prediction_id',
      as: 'prediction',
    });
  };

  return Match;
};
