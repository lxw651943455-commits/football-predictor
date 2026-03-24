/**
 * Team Model
 * Stores team information and statistics
 */

import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const Team = sequelize.define('Team', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },

    // External ID
    api_football_team_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
      unique: true,
    },

    // Team details
    name: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
    },

    short_name: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    logo: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    league: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    league_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    // Current season stats
    league_position: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    matches_played: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    wins: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    draws: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    losses: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    goals_for: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    goals_against: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    goal_difference: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    points: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    // Form (last 5 matches)
    form: {
      type: DataTypes.STRING,
      allowNull: true,
      validate: {
        isIn: [['W', 'D', 'L', 'W', 'D']],
      },
    },

    // Home/Away records
    home_wins: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    home_draws: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    home_losses: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    away_wins: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    away_draws: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    away_losses: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    // Manager info
    manager_name: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    manager_style: {
      type: DataTypes.ENUM('attacking', 'defensive', 'balanced', 'counter'),
      allowNull: true,
    },

    // Stadium
    stadium_name: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    stadium_capacity: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    // Metadata
    founded_year: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    country: {
      type: DataTypes.STRING,
      allowNull: true,
    },
  }, {
    tableName: 'teams',
    indexes: [
      { fields: ['name'] },
      { fields: ['league'] },
      { fields: ['league_position'] },
      { fields: ['points'] },
    ],
  });

  Team.associate = () => {
    // Add associations if needed
  };

  return Team;
};
