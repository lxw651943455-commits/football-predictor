/**
 * Referee Model
 * Stores referee information and statistics
 */

import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const Referee = sequelize.define('Referee', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },

    // External ID
    api_football_referee_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
      unique: true,
    },

    // Referee details
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },

    nationality: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    // Statistics
    total_matches: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    avg_home_yellows: {
      type: DataTypes.FLOAT,
      defaultValue: 2.5,
    },

    avg_away_yellows: {
      type: DataTypes.FLOAT,
      defaultValue: 2.5,
    },

    red_card_rate: {
      type: DataTypes.FLOAT,
      defaultValue: 0.02,
    },

    penalty_rate: {
      type: DataTypes.FLOAT,
      defaultValue: 0.10,
    },

    // Bias indicator (cards per team ratio)
    home_bias_score: {
      type: DataTypes.FLOAT,
      allowNull: true,
      comment: 'Positive = favors home, Negative = favors away',
    },

    // Photo
    photo: {
      type: DataTypes.STRING,
      allowNull: true,
    },
  }, {
    tableName: 'referees',
    indexes: [
      { fields: ['name'] },
      { fields: ['nationality'] },
    ],
  });

  Referee.associate = () => {
    // Add associations if needed
  };

  return Referee;
};
