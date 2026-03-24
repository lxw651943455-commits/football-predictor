/**
 * OddsHistory Model
 * Stores historical odds data for trend analysis
 */

import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const OddsHistory = sequelize.define('OddsHistory', {
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

    // Bookmaker
    bookmaker: {
      type: DataTypes.STRING,
      allowNull: false,
    },

    // Odds values
    home_odds: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    draw_odds: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    away_odds: {
      type: DataTypes.FLOAT,
      allowNull: false,
    },

    // Handicap
    asian_handicap_home: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    asian_handicap_away: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    // Over/Under
    over_2_5: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    under_2_5: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    // Timestamp
    recorded_at: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW,
      index: true,
    },

    // Is opening odds
    is_opening: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },
  }, {
    tableName: 'odds_history',
    indexes: [
      { fields: ['match_id'] },
      { fields: ['bookmaker'] },
      { fields: ['recorded_at'] },
      { fields: ['match_id', 'bookmaker', 'recorded_at'] },
    ],
  });

  OddsHistory.associate = () => {
    // Add associations if needed
  };

  return OddsHistory;
};
