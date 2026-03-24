import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatPercentage(value) {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

export function getWinnerLabel(winner) {
  const labels = {
    home: 'Home Win',
    draw: 'Draw',
    away: 'Away Win',
  };
  return labels[winner] || winner;
}

export function getDimensionLabel(key) {
  const labels = {
    odds: 'Odds Market',
    injuries: 'Injuries',
    players: 'Player Form',
    tactics: 'Tactics',
    home_advantage: 'Home Advantage',
    referee: 'Referee',
    h2h: 'Head-to-Head',
    motivation: 'Motivation',
    fitness: 'Fitness',
  };
  return labels[key] || key;
}
