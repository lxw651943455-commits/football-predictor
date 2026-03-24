"""
Nine-Dimensional Holistic Match Prediction Model
九维全息赛事演算模型

Based on the user's football prediction framework that analyzes matches beyond basic stats,
focusing on dimension differences and fitness accumulation over time.

Nine Dimensions:
1. 盘口赔率 - Odds market analysis and trends
2. 伤停情报 - Injury and suspension analysis
3. 球员对位 - Player matchups and form
4. 战术相克 - Manager tactical compatibility
5. 主场优势 - Home advantage and stadium factor
6. 裁判因素 - Referee style and card tendencies
7. 历史交锋 - Head-to-head history and psychological advantage
8. 赛事战意 - Match motivation based on league/cup context
9. 体能状况 - Fitness level based on recent schedule density
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class MatchData:
    """Complete match data for prediction"""
    # Basic info
    home_team: str
    away_team: str
    league: str
    match_date: datetime

    # Dimension 1: Odds data
    home_odds: float  # Home win decimal odds
    draw_odds: float
    away_odds: float
    opening_home_odds: Optional[float] = None
    opening_draw_odds: Optional[float] = None
    opening_away_odds: Optional[float] = None
    asian_handicap: Optional[float] = None
    over_under: Optional[float] = None

    # Dimension 2: Injuries and suspensions
    home_injuries: List[Dict] = None
    away_injuries: List[Dict] = None
    home_suspensions: List[Dict] = None
    away_suspensions: List[Dict] = None

    # Dimension 3: Player matchups
    home_lineup: List[Dict] = None
    away_lineup: List[Dict] = None
    home_form: List[str] = None  # Last 5 results: ['W', 'D', 'L', 'W', 'W']
    away_form: List[str] = None

    # Dimension 4: Manager tactics
    home_manager: Optional[Dict] = None
    away_manager: Optional[Dict] = None

    # Dimension 5: Home advantage
    home_stadium: Optional[str] = None
    home_home_record: Optional[Dict] = None  # {'wins': 10, 'draws': 3, 'losses': 2}
    away_away_record: Optional[Dict] = None

    # Dimension 6: Referee
    referee: Optional[Dict] = None

    # Dimension 7: Head-to-head
    h2h_matches: List[Dict] = None

    # Dimension 8: Match motivation
    home_league_position: Optional[int] = None
    away_league_position: Optional[int] = None
    is_cup_match: bool = False
    is_relegation_fight: bool = False
    is_title_race: bool = False

    # Dimension 9: Fitness
    home_last_match_date: Optional[datetime] = None
    away_last_match_date: Optional[datetime] = None
    home_matches_last_14_days: int = 0
    away_matches_last_14_days: int = 0
    home_travel_distance_km: Optional[float] = None

    def __post_init__(self):
        if self.home_injuries is None:
            self.home_injuries = []
        if self.away_injuries is None:
            self.away_injuries = []
        if self.home_suspensions is None:
            self.home_suspensions = []
        if self.away_suspensions is None:
            self.away_suspensions = []
        if self.home_lineup is None:
            self.home_lineup = []
        if self.away_lineup is None:
            self.away_lineup = []
        if self.home_form is None:
            self.home_form = []
        if self.away_form is None:
            self.away_form = []
        if self.h2h_matches is None:
            self.h2h_matches = []


@dataclass
class PredictionResult:
    """Prediction result with nine-dimensional scores"""
    home_team: str
    away_team: str
    match_date: datetime

    # Nine dimension scores (0-1)
    dimension_scores: Dict[str, float]

    # Prediction outcomes
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_score: str
    predicted_winner: str  # 'home', 'draw', 'away'

    # Confidence and insights
    overall_confidence: float  # 0-1
    key_insights: List[str]
    risk_factors: List[str]

    # Recommended bet
    recommended_bet: Optional[str] = None  # 'home', 'draw', 'away', 'over', 'under'
    bet_confidence: Optional[float] = None


class NineDimensionPredictor:
    """
    Nine-Dimensional Holistic Match Prediction Engine
    九维全息赛事演算引擎
    """

    # Default weights for each dimension (adjustable)
    DEFAULT_WEIGHTS = {
        'odds': 0.15,           # Market wisdom
        'injuries': 0.12,       # Player availability
        'players': 0.10,        # Form and matchups
        'tactics': 0.08,        # Manager tactical battle
        'home_advantage': 0.12, # Home field factor
        'referee': 0.05,        # Referee style
        'h2h': 0.13,           # Historical psychological edge
        'motivation': 0.15,     # Match importance (CRITICAL)
        'fitness': 0.10,        # Physical condition (CRITICAL)
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize predictor with custom weights

        Args:
            weights: Custom dimension weights (must sum to 1.0)
        """
        if weights:
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                raise ValueError(f"Weights must sum to 1.0, got {total}")
            self.weights = weights
        else:
            self.weights = self.DEFAULT_WEIGHTS.copy()

    def predict(self, match_data: MatchData) -> PredictionResult:
        """
        Generate full prediction using all nine dimensions

        Args:
            match_data: Complete match data

        Returns:
            PredictionResult with scores and insights
        """
        # Calculate dimension scores
        dimension_scores = {
            'odds': self._analyze_odds_market(match_data),
            'injuries': self._analyze_injuries(match_data),
            'players': self._analyze_players(match_data),
            'tactics': self._analyze_tactics(match_data),
            'home_advantage': self._analyze_home_advantage(match_data),
            'referee': self._analyze_referee(match_data),
            'h2h': self._analyze_h2h(match_data),
            'motivation': self._analyze_motivation(match_data),
            'fitness': self._analyze_fitness(match_data),
        }

        # Calculate weighted home advantage score
        home_advantage_score = sum(
            dimension_scores[dim] * self.weights[dim]
            for dim in dimension_scores
        )

        # Convert to probabilities
        home_prob, draw_prob, away_prob = self._scores_to_probabilities(
            home_advantage_score, match_data
        )

        # Generate predicted score
        predicted_score = self._predict_score(
            home_prob, draw_prob, away_prob, match_data
        )

        # Determine winner
        if home_prob > draw_prob and home_prob > away_prob:
            predicted_winner = 'home'
        elif away_prob > draw_prob:
            predicted_winner = 'away'
        else:
            predicted_winner = 'draw'

        # Generate insights
        key_insights, risk_factors = self._generate_insights(
            match_data, dimension_scores
        )

        # Calculate confidence based on dimension agreement
        confidence = self._calculate_confidence(dimension_scores)

        # Generate bet recommendation
        recommended_bet, bet_confidence = self._recommend_bet(
            home_prob, draw_prob, away_prob, match_data, dimension_scores
        )

        return PredictionResult(
            home_team=match_data.home_team,
            away_team=match_data.away_team,
            match_date=match_data.match_date,
            dimension_scores=dimension_scores,
            home_win_probability=round(home_prob, 3),
            draw_probability=round(draw_prob, 3),
            away_win_probability=round(away_prob, 3),
            predicted_score=predicted_score,
            predicted_winner=predicted_winner,
            overall_confidence=round(confidence, 3),
            key_insights=key_insights,
            risk_factors=risk_factors,
            recommended_bet=recommended_bet,
            bet_confidence=round(bet_confidence, 3) if bet_confidence else None,
        )

    # ========== Dimension 1: Odds Market Analysis ==========

    def _analyze_odds_market(self, data: MatchData) -> float:
        """
        Analyze odds market trends and implied probabilities
        0 = favor away, 0.5 = neutral, 1 = favor home
        """
        # Convert odds to implied probabilities
        total = data.home_odds + data.draw_odds + data.away_odds
        home_implied = (1 / data.home_odds) / total
        away_implied = (1 / data.away_odds) / total

        # Check for odds movement (market sentiment)
        if data.opening_home_odds:
            opening_diff = data.opening_home_odds - data.home_odds
            # Odds dropping = more money on home = positive for home
            movement_factor = min(opening_diff / 0.5, 0.1)  # Max 10% adjustment
        else:
            movement_factor = 0

        # Calculate score
        base_score = home_implied / (home_implied + away_implied)
        final_score = np.clip(base_score + movement_factor, 0, 1)

        return final_score

    # ========== Dimension 2: Injury & Suspension Analysis ==========

    def _analyze_injuries(self, data: MatchData) -> float:
        """
        Analyze impact of injuries and suspensions
        Returns home advantage score (0-1)
        """
        # Calculate injury impact scores
        home_impact = sum(
            self._calculate_player_impact(player)
            for player in data.home_injuries + data.home_suspensions
        )
        away_impact = sum(
            self._calculate_player_impact(player)
            for player in data.away_injuries + data.away_suspensions
        )

        # Normalize (assuming max reasonable impact is ~50 points)
        max_impact = 50
        home_normalized = min(home_impact / max_impact, 1)
        away_normalized = min(away_impact / max_impact, 1)

        # More injuries for away team = higher home advantage
        if home_normalized + away_normalized == 0:
            return 0.5  # No injuries = neutral

        score = 0.5 + (away_normalized - home_normalized) * 0.4
        return np.clip(score, 0, 1)

    def _calculate_player_impact(self, player: Dict) -> float:
        """Calculate impact value of injured/suspended player (0-50)"""
        impact = 0

        # Key positions matter more
        position = player.get('position', '').lower()
        if position in ['goalkeeper', 'gk']:
            impact = 20
        elif position in ['defender', 'centre-back', 'full-back']:
            impact = 12
        elif position in ['midfielder']:
            impact = 15
        elif position in ['forward', 'striker', 'winger']:
            impact = 18

        # Stars matter more
        if player.get('is_key_player', False):
            impact *= 1.5

        # Long-term injuries already factored into team form
        if player.get('days_out', 0) > 30:
            impact *= 0.5

        return impact

    # ========== Dimension 3: Player Matchups & Form ==========

    def _analyze_players(self, data: MatchData) -> float:
        """Analyze player form and matchups"""
        if not data.home_form or not data.away_form:
            return 0.5

        # Calculate form points (W=3, D=1, L=0)
        def form_points(form_list):
            points = {'W': 3, 'D': 1, 'L': 0}
            return sum(points.get(r, 0) for r in form_list[-5:])  # Last 5 matches

        home_points = form_points(data.home_form)
        away_points = form_points(data.away_form)

        if home_points + away_points == 0:
            return 0.5

        score = home_points / (home_points + away_points)
        return np.clip(score, 0.2, 0.8)  # Don't be too extreme

    # ========== Dimension 4: Tactical Matchup ==========

    def _analyze_tactics(self, data: MatchData) -> float:
        """
        Analyze manager tactical matchup
        This is a simplified version - full version would track historical matchups
        """
        if not data.home_manager or not data.away_manager:
            return 0.5

        # Manager experience advantage
        home_experience = data.home_manager.get('years_experience', 0)
        away_experience = data.away_manager.get('years_experience', 0)

        if home_experience + away_experience == 0:
            base_score = 0.5
        else:
            base_score = home_experience / (home_experience + away_experience)

        # Tactical style factors (attack vs defense)
        home_style = data.home_manager.get('style', 'balanced')
        away_style = data.away_manager.get('style', 'balanced')

        # Counter-attacking away teams can neutralize home advantage
        if home_style == 'attacking' and away_style == 'counter':
            style_factor = -0.1
        elif home_style == 'counter' and away_style == 'attacking':
            style_factor = 0.1
        else:
            style_factor = 0

        return np.clip(base_score + style_factor, 0, 1)

    # ========== Dimension 5: Home Advantage ==========

    def _analyze_home_advantage(self, data: MatchData) -> float:
        """Analyze home field advantage based on historical records"""
        if not data.home_home_record or not data.away_away_record:
            return 0.6  # Default home advantage

        # Home team's home performance
        home_total = sum(data.home_home_record.values())
        if home_total == 0:
            home_home_pct = 0.6
        else:
            home_home_pct = (
                data.home_home_record.get('wins', 0) * 3 +
                data.home_home_record.get('draws', 0)
            ) / (home_total * 3)

        # Away team's away performance
        away_total = sum(data.away_away_record.values())
        if away_total == 0:
            away_away_pct = 0.4
        else:
            away_away_pct = (
                data.away_away_record.get('wins', 0) * 3 +
                data.away_away_record.get('draws', 0)
            ) / (away_total * 3)

        # Calculate advantage
        if home_home_pct + away_away_pct == 0:
            return 0.6

        score = home_home_pct / (home_home_pct + away_away_pct)
        return np.clip(score, 0.4, 0.8)

    # ========== Dimension 6: Referee Factor ==========

    def _analyze_referee(self, data: MatchData) -> float:
        """
        Analyze referee impact on match
        Some referees favor home teams, some are card-happy affecting physical play
        """
        if not data.referee:
            return 0.5

        # Referee home bias (yellow cards per team ratio)
        home_cards = data.referee.get('avg_home_yellows', 2.5)
        away_cards = data.referee.get('avg_away_yellows', 2.5)

        if home_cards + away_cards == 0:
            return 0.5

        # More away cards = home advantage
        bias_factor = 1 - (home_cards / (home_cards + away_cards))

        # Red card tendency (affects favorites)
        red_rate = data.referee.get('red_card_rate', 0.02)
        if red_rate > 0.05:
            # High card rate increases variance (helps underdog/away)
            variance_factor = -0.1
        else:
            variance_factor = 0

        return np.clip(0.5 + bias_factor * 0.1 + variance_factor, 0.3, 0.7)

    # ========== Dimension 7: Head-to-Head History ==========

    def _analyze_h2h(self, data: MatchData) -> float:
        """
        Analyze historical head-to-head for psychological advantage
        '血脉压制' (bloodline suppression) - one team consistently beats another
        """
        if not data.h2h_matches:
            return 0.5

        # Look at recent H2H (last 10 matches)
        recent_h2h = data.h2h_matches[-10:]

        home_wins = sum(1 for m in recent_h2h if m.get('winner') == 'home')
        away_wins = sum(1 for m in recent_h2h if m.get('winner') == 'away')

        if home_wins + away_wins == 0:
            return 0.5

        h2h_score = home_wins / (home_wins + away_wins)

        # Check for 'bloodline suppression' (dominance)
        if home_wins >= len(recent_h2h) * 0.7:
            # Home dominates away
            return min(h2h_score + 0.1, 0.9)
        elif away_wins >= len(recent_h2h) * 0.7:
            # Away dominates home
            return max(h2h_score - 0.1, 0.1)

        return h2h_score

    # ========== Dimension 8: Match Motivation (CRITICAL) ==========

    def _analyze_motivation(self, data: MatchData) -> float:
        """
        Analyze match motivation and strategic priority
        This is CRITICAL - Champions League gene vs relegation
        """
        score = 0.5

        # League position gap
        if data.home_league_position and data.away_league_position:
            position_diff = data.away_league_position - data.home_league_position

            # Better home team = higher score
            position_factor = np.tanh(position_diff / 10) * 0.3
            score += position_factor

        # Title race motivation
        if data.is_title_race:
            if data.home_league_position and data.home_league_position <= 3:
                score += 0.15  # Home team fighting for title

        # Relegation fight motivation
        if data.is_relegation_fight:
            if data.home_league_position and data.home_league_position >= data.away_league_position:
                score += 0.1  # Home team more desperate

        # Cup match variance
        if data.is_cup_match:
            # Cup matches are more unpredictable
            score = 0.5  # Reset to neutral

            # But if one team is in relegation fight, they might prioritize league
            if data.is_relegation_fight:
                # Which team is more likely to prioritize league?
                if data.home_league_position and data.home_league_position >= 18:
                    score -= 0.15  # Home might rotate squad

        return np.clip(score, 0.2, 0.8)

    # ========== Dimension 9: Fitness & Schedule Density (CRITICAL) ==========

    def _analyze_fitness(self, data: MatchData) -> float:
        """
        Analyze fitness levels based on recent schedule
        This is CRITICAL - '魔鬼赛程' (devil schedule) causes collapses
        """
        score = 0.5

        # Match density in last 14 days
        home_density = data.home_matches_last_14_days
        away_density = data.away_matches_last_14_days

        # Penalty for heavy schedule
        if home_density > 4:
            # Home team exhausted - potential collapse
            fatigue_penalty = (home_density - 4) * 0.08
            score -= fatigue_penalty

        if away_density > 4:
            # Away team exhausted + travel = double penalty
            fatigue_penalty = (away_density - 4) * 0.10
            score += fatigue_penalty

        # Recovery time since last match
        if data.home_last_match_date and data.away_last_match_date:
            home_rest = (data.match_date - data.home_last_match_date).days
            away_rest = (data.match_date - data.away_last_match_date).days

            rest_diff = home_rest - away_rest
            # More rest = advantage
            score += np.tanh(rest_diff / 3) * 0.15

        # Travel fatigue for away team
        if data.home_travel_distance_km:
            if data.home_travel_distance_km > 2000:
                # Long trip + away = major disadvantage
                score += 0.15
            elif data.home_travel_distance_km > 500:
                score += 0.05

        # Critical: '欧冠后遗症' (Champions League hangover)
        # If home team played Champions League midweek
        if home_density >= 2:
            # Potential for 'black weekend' - big favorite losing
            score -= 0.1

        return np.clip(score, 0.1, 0.9)

    # ========== Helper Methods ==========

    def _scores_to_probabilities(
        self,
        home_advantage_score: float,
        data: MatchData
    ) -> Tuple[float, float, float]:
        """Convert home advantage score to win/draw/loss probabilities"""
        # Base probabilities from odds
        total_odds = data.home_odds + data.draw_odds + data.away_odds
        base_home = (1 / data.home_odds) / total_odds
        base_draw = (1 / data.draw_odds) / total_odds
        base_away = (1 / data.away_odds) / total_odds

        # Adjust based on nine-dimensional score
        # Score < 0.5 favors away, > 0.5 favors home
        adjustment_factor = (home_advantage_score - 0.5) * 0.4

        adjusted_home = base_home + adjustment_factor
        adjusted_away = base_away - adjustment_factor
        adjusted_draw = base_draw

        # Normalize
        total = adjusted_home + adjusted_draw + adjusted_away
        return (
            max(0, adjusted_home / total),
            max(0, adjusted_draw / total),
            max(0, adjusted_away / total)
        )

    def _predict_score(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        data: MatchData
    ) -> str:
        """Predict most likely scoreline with intelligent goal distribution"""
        # Calculate expected goals based on odds
        # Lower odds = stronger team = more goals expected

        # Base expected goals from odds strength
        if data.home_odds < 1.5:
            # Home strong
            home_expected = 2.2
            away_expected = max(0.5, 3.0 - data.home_odds)
        elif data.away_odds < 1.5:
            # Away strong
            away_expected = 2.2
            home_expected = max(0.5, 3.0 - data.away_odds)
        else:
            # More balanced match
            total_from_odds = (1 / data.home_odds + 1 / data.away_odds) * 3.5
            home_strength = (1 / data.home_odds) / (1 / data.home_odds + 1 / data.away_odds)
            home_expected = total_from_odds * home_strength
            away_expected = total_from_odds * (1 - home_strength)

        # Adjust for draw probability
        if draw_prob > 0.3:
            # High draw probability = tighter match = fewer goals
            home_expected *= 0.85
            away_expected *= 0.85

        # Round to reasonable goal numbers
        home_goals = max(0, round(home_expected))
        away_goals = max(0, round(away_expected))

        # Cap extreme scores
        if home_goals > 5:
            home_goals = 5
        if away_goals > 5:
            away_goals = 5

        # Most common scorelines adjustment
        # If probabilities are close, lean toward draw-like scores
        if abs(home_prob - away_prob) < 0.1:
            # Very close match - likely 1-1, 1-0, 0-0, 2-1
            if draw_prob > 0.35:
                # High draw probability
                common_scores = [(1, 1), (1, 0), (0, 0), (2, 1), (1, 2)]
            else:
                common_scores = [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2), (2, 0)]

            # Choose score closest to our calculation
            min_diff = float('inf')
            best_score = (home_goals, away_goals)
            for score in common_scores:
                diff = abs(score[0] - home_expected) + abs(score[1] - away_expected)
                if diff < min_diff:
                    min_diff = diff
                    best_score = score

            home_goals, away_goals = best_score

        # Ensure we don't have 0-0 for strong favorite matches
        if (data.home_odds < 1.8 or data.away_odds < 1.8) and home_goals + away_goals == 0:
            if data.home_odds < data.away_odds:
                home_goals = 1
            else:
                away_goals = 1

        # Predict final score
        predicted = f"{home_goals}-{away_goals}"

        return predicted

    def _calculate_confidence(self, dimension_scores: Dict[str, float]) -> float:
        """Calculate overall confidence based on dimension agreement"""
        # Calculate standard deviation - lower = more agreement = higher confidence
        scores = list(dimension_scores.values())
        std_dev = np.std(scores)

        # Convert to confidence (0-1)
        # Low std_dev (<0.15) = high confidence
        # High std_dev (>0.3) = low confidence
        confidence = 1 - np.clip((std_dev - 0.15) / 0.15, 0, 1)
        return confidence

    def _generate_insights(
        self,
        data: MatchData,
        scores: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Generate key insights and risk factors"""
        insights = []
        risks = []

        # Odds movement insight
        if data.opening_home_odds and data.home_odds:
            if data.opening_home_odds > data.home_odds + 0.2:
                insights.append(f"Market moving towards {data.home_team} (odds dropped)")
            elif data.opening_home_odds < data.home_odds - 0.2:
                insights.append(f"Market moving towards {data.away_team} (odds drifted)")

        # Injury insight
        if data.home_injuries or data.home_suspensions:
            impact = sum(self._calculate_player_impact(p)
                        for p in data.home_injuries + data.home_suspensions)
            if impact > 20:
                risks.append(f"{data.home_team} missing key players ({impact} points)")

        # Motivation insight
        if data.is_cup_match and data.is_relegation_fight:
            risks.append("Cup match - possible squad rotation for relegation battler")

        # Fitness insight
        if data.home_matches_last_14_days >= 5:
            risks.append(f"{data.home_team} on heavy schedule (5+ matches in 14 days) - fatigue risk")

        # H2H dominance
        if data.h2h_matches:
            recent = data.h2h_matches[-5:]
            home_wins = sum(1 for m in recent if m.get('winner') == 'home')
            away_wins = sum(1 for m in recent if m.get('winner') == 'away')
            if home_wins >= 4:
                insights.append(f"{data.home_team} has strong H2H dominance (4+/5)")
            elif away_wins >= 4:
                insights.append(f"{data.away_team} has strong H2H dominance (4+/5)")

        # Home advantage insight
        if scores.get('home_advantage', 0.5) > 0.7:
            insights.append(f"{data.home_team} has exceptional home record")

        return insights, risks

    def _recommend_bet(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        data: MatchData,
        scores: Dict[str, float]
    ) -> Tuple[Optional[str], Optional[float]]:
        """Generate bet recommendation with confidence"""
        probs = {
            'home': home_prob,
            'draw': draw_prob,
            'away': away_prob
        }

        # Find highest probability
        max_outcome = max(probs, key=probs.get)
        max_prob = probs[max_outcome]

        # Minimum threshold for recommendation
        if max_prob < 0.4:
            return None, None

        # Check for value bet (probability > implied probability from odds)
        implied_home = 1 / data.home_odds
        implied_draw = 1 / data.draw_odds
        implied_away = 1 / data.away_odds

        implied = {
            'home': implied_home,
            'draw': implied_draw,
            'away': implied_away
        }

        if max_prob > implied[max_outcome]:
            # Value bet found
            confidence = (max_prob - implied[max_outcome]) * 2
            return max_outcome, min(confidence, 1)

        return None, None


# Convenience function for quick predictions
def quick_predict(
    home_team: str,
    away_team: str,
    home_odds: float,
    draw_odds: float,
    away_odds: float,
    **kwargs
) -> PredictionResult:
    """
    Quick prediction function with minimal required data

    Args:
        home_team: Home team name
        away_team: Away team name
        home_odds: Home win decimal odds
        draw_odds: Draw decimal odds
        away_odds: Away win decimal odds
        **kwargs: Optional additional data

    Returns:
        PredictionResult
    """
    match_data = MatchData(
        home_team=home_team,
        away_team=away_team,
        league=kwargs.get('league', 'Unknown'),
        match_date=kwargs.get('match_date', datetime.now()),
        home_odds=home_odds,
        draw_odds=draw_odds,
        away_odds=away_odds,
        opening_home_odds=kwargs.get('opening_home_odds'),
        opening_draw_odds=kwargs.get('opening_draw_odds'),
        opening_away_odds=kwargs.get('opening_away_odds'),
        home_form=kwargs.get('home_form', []),
        away_form=kwargs.get('away_form', []),
        home_league_position=kwargs.get('home_league_position'),
        away_league_position=kwargs.get('away_league_position'),
        is_cup_match=kwargs.get('is_cup_match', False),
        home_matches_last_14_days=kwargs.get('home_matches_last_14_days', 0),
        away_matches_last_14_days=kwargs.get('away_matches_last_14_days', 0),
    )

    predictor = NineDimensionPredictor()
    return predictor.predict(match_data)


if __name__ == "__main__":
    # Example usage
    print("Nine-Dimensional Football Prediction Model")
    print("=" * 50)

    # Example: Premier League match
    result = quick_predict(
        home_team="Arsenal",
        away_team="Chelsea",
        home_odds=2.10,
        draw_odds=3.40,
        away_odds=3.60,
        league="Premier League",
        home_form=['W', 'W', 'D', 'W', 'L'],
        away_form=['W', 'L', 'W', 'D', 'W'],
        home_league_position=2,
        away_league_position=5,
        home_matches_last_14_days=3,
        away_matches_last_14_days=3,
    )

    print(f"\nMatch: {result.home_team} vs {result.away_team}")
    print(f"Predicted Score: {result.predicted_score}")
    print(f"Winner: {result.predicted_winner}")
    print(f"\nProbabilities:")
    print(f"  Home: {result.home_win_probability:.1%}")
    print(f"  Draw: {result.draw_probability:.1%}")
    print(f"  Away: {result.away_win_probability:.1%}")
    print(f"\nDimension Scores:")
    for dim, score in result.dimension_scores.items():
        print(f"  {dim}: {score:.2f}")
    print(f"\nConfidence: {result.overall_confidence:.1%}")
    if result.recommended_bet:
        print(f"Recommended Bet: {result.recommended_bet} ({result.bet_confidence:.1%})")
    print(f"\nKey Insights:")
    for insight in result.key_insights:
        print(f"  • {insight}")
    if result.risk_factors:
        print(f"\nRisk Factors:")
        for risk in result.risk_factors:
            print(f"  ⚠ {risk}")
