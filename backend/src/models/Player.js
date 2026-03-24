/**
 * Player Model
 * Stores player information and injury status
 */

import { DataTypes } from 'sequelize';

export default (sequelize) => {
  const Player = sequelize.define('Player', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },

    // External ID
    api_football_player_id: {
      type: DataTypes.INTEGER,
      allowNull: true,
      unique: true,
    },

    // Player details
    name: {
      type: DataTypes.STRING,
      allowNull: false,
    },

    team: {
      type: DataTypes.STRING,
      allowNull: true,
      index: true,
    },

    team_id: {
      type: DataTypes.UUID,
      allowNull: true,
      references: {
        model: 'teams',
        key: 'id',
      },
    },

    // Position
    position: {
      type: DataTypes.ENUM(
        'goalkeeper',
        'centre-back',
        'full-back',
        'defensive-midfield',
        'central-midfield',
        'attacking-midfield',
        'winger',
        'forward',
        'striker'
      ),
      allowNull: true,
    },

    // Status
    is_key_player: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },

    is_injured: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },

    is_suspended: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
    },

    injury_type: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    injury_start_date: {
      type: DataTypes.DATE,
      allowNull: true,
    },

    expected_return_date: {
      type: DataTypes.DATE,
      allowNull: true,
    },

    days_out: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    // Stats
    age: {
      type: DataTypes.INTEGER,
      allowNull: true,
    },

    nationality: {
      type: DataTypes.STRING,
      allowNull: true,
    },

    appearances: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    goals: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    assists: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
    },

    // Market value (optional)
    market_value: {
      type: DataTypes.FLOAT,
      allowNull: true,
    },

    // Photo
    photo: {
      type: DataTypes.STRING,
      allowNull: true,
    },
  }, {
    tableName: 'players',
    indexes: [
      { fields: ['name'] },
      { fields: ['team'] },
      { fields: ['is_injured'] },
      { fields: ['is_suspended'] },
      { fields: ['is_key_player'] },
    ],
  });

  Player.associate = () => {
    // Add associations if needed
  };

  return Player;
};
