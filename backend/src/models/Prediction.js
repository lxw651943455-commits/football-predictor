/**
 * Prediction Model
 * Stores prediction results with nine-dimensional scores
 */

import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const Prediction = sequelize.define('Prediction', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },

    // Match reference
    match_id: {
      type: DataTypes.STRING,
      allowNull: false,
      index: true,
    },

    // Team information
    home_team: {
      type: DataTypes.STRING,
      allowNull: false,
    },

    away_team: {
      type: DataTypes.STRING,
      allowNull: false,
    },

    league: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    match_date: {
      type: DataTypes.DATE,
      allowNull: false,
      index: true,
    },

    // Nine-dimensional scores (0-1)
    dimension_odds: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_odds',
    },

    dimension_injuries: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_injuries',
    },

    dimension_players: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_players',
    },

    dimension_tactics: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_tactics',
    },

    dimension_home_advantage: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_home_advantage',
    },

    dimension_referee: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_referee',
    },

    dimension_h2h: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_h2h',
    },

    dimension_motivation: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_motivation',
    },

    dimension_fitness: {
      type: DataTypes.FLOAT,
      allowNull: true,
      field: 'dimension_fitness',
    },

    // Prediction outcomes
    home_win_probability: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    draw_probability: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    away_win_probability: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    predicted_score: {
      type: DataTypes.STRING,
      allowNull: false,
    },

    predicted_winner: {
      type: DataTypes.ENUM('home', 'draw', 'away'),
      allowNull: false,
    },

    // Confidence and insights
    overall_confidence: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    key_insights: {
      type: DataTypes.JSON,
      allowNull: true,
      defaultValue: [],
    },

    risk_factors: {
      type: DataTypes.JSON,
      allowNull: true,
      defaultValue: [],
    },

    // Bet recommendation
    recommended_bet: {
      type: DataTypes.ENUM('home', 'draw', 'away', 'over', 'under', null),
      allowNull: true,
    },

    bet_confidence: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    // Actual result (for accuracy tracking)
    actual_score: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    actual_winner: {
      type: DataTypes.ENUM('home', 'draw', 'away', null),
      allowNull: true,
    },

    is_correct: {
      type: DataTypes.BOOLEAN,
      allowNull: true,
    },

    // Metadata
    prediction_model: {
      type: DataTypes.STRING,
      defaultValue: 'nine_dimensions_v1',
    },

    custom_weights: {
      type: DataTypes.JSON,
      allowNull: true,
    },
  }, {
    tableName: 'predictions',
    indexes: [
      { fields: ['match_date'] },
      { fields: ['home_team'] },
      { fields: ['away_team'] },
      { fields: ['predicted_winner'] },
      { fields: ['is_correct'] },
      { fields: ['created_at'] },
    ],
  });

  Prediction.associate = (models) => {
    // Association with Match (if we have a Match model)
    if (models.Match) {
      Prediction.hasOne(models.Match, {
        foreignKey: 'prediction_id',
        as: 'match',
      });
    }
  };

  return Prediction;
};
