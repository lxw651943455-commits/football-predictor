"""
Flask API Server for Prediction Engine
Serves the nine-dimensional prediction model as a REST API

NEW FLOW (20-40 seconds):
1. Fetch realtime data from API-Football (15-30 seconds)
2. Generate LLM analysis using ZhipuAI/MiniMax (5-10 seconds)
3. Output final prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from typing import Dict, Any, List
import asyncio
import time

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# 立即写入启动日志
try:
    with open('flask_startup.log', 'a') as f:
        f.write(f"\n[{datetime.now()}] main.py imported\n")
except:
    pass

from models.nine_dimensions import NineDimensionPredictor, MatchData
from services.realtime_data_fetcher import fetch_all_realtime_data
from services.llm_analyzer import generate_llm_analysis

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize predictor (lazy load)
predictor: NineDimensionPredictor = None


def get_predictor() -> NineDimensionPredictor:
    """Get or initialize predictor"""
    global predictor
    if predictor is None:
        predictor = NineDimensionPredictor()
    return predictor


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'prediction-engine'
    })


@app.route('/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables"""
    return jsonify({
        'zhipu_api_key_set': bool(os.getenv('ZHIPU_API_KEY')),
        'zhipu_api_key_prefix': os.getenv('ZHIPU_API_KEY', '')[:20] if os.getenv('ZHIPU_API_KEY') else None,
        'minimax_api_key_set': bool(os.getenv('MINIMAX_API_KEY')),
        'minimax_api_key_prefix': os.getenv('MINIMAX_API_KEY', '')[:20] if os.getenv('MINIMAX_API_KEY') else None,
        'working_dir': os.getcwd(),
    })


@app.route('/api/predict', methods=['POST'])
def predict_match():
    """
    Generate prediction for a match with REALTIME data and LLM analysis

    NEW FLOW (20-40 seconds):
    1. Fetch realtime data (15-30s)
    2. Nine-dimensional analysis (2-3s)
    3. LLM deep analysis (5-10s)

    Expected JSON body:
    {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "league": "Premier League",
        "home_odds": 2.10,
        "draw_odds": 3.40,
        "away_odds": 3.60
    }
    """
    # 立即写入日志 - 在函数最开始
    open('predict_called.txt', 'w').close()  # 创建一个标记文件
    open('debug_main.txt', 'a').write(f"\n[{datetime.now()}] PREDICT_MATCH ENTRY\n")

    print("\n" + "="*60)
    print("STARTING PREDICTION FLOW")
    print("="*60)

    total_start = time.time()

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        home_team = data['home_team']
        away_team = data['away_team']
        league = data.get('league', 'Premier League')

        print(f"Match: {home_team} vs {away_team}")
        print(f"League: {league}")

        # ========== STEP 1: Fetch Realtime Data ==========
        print("\n" + "="*60)
        print("STEP 1: Fetching match data (auto-fallback)")
        print("="*60)

        # Log before calling data source
        with open('debug_main.txt', 'a') as f:
            f.write(f"About to call fetch_match_data_sync\n")
            f.flush()

        from services.data_source_manager import fetch_match_data_sync

        # Use synchronous wrapper for Flask
        realtime_data = fetch_match_data_sync(home_team, away_team, league)

        # Log after calling data source
        with open('debug_main.txt', 'a') as f:
            f.write(f"fetch_match_data_sync returned\n")
            f.write(f"data_source: {realtime_data.get('data_source')}\n")
            f.write(f"h2h count: {len(realtime_data.get('h2h_matches', []))}\n")
            f.flush()

        if not realtime_data:
            return jsonify({'error': 'Failed to fetch match data'}), 500

        # Log data source used
        data_source = realtime_data.get('data_source', 'unknown')
        print(f"\n[Data Source] Using: {data_source.upper()}")

        # ========== STEP 2: Nine-Dimensional Analysis ==========
        print("\n" + "="*60)
        print("STEP 2: Nine-dimensional calculation")
        print("="*60)

        # Create predictor
        predictor_instance = get_predictor()
        if 'weights' in data:
            from models.nine_dimensions import NineDimensionPredictor
            predictor_instance = NineDimensionPredictor(weights=data['weights'])

        # Build form from stats
        home_stats = realtime_data.get('home_stats', {})
        away_stats = realtime_data.get('away_stats', {})

        # Calculate form from stats
        home_form = _calculate_form_from_stats(home_stats)
        away_form = _calculate_form_from_stats(away_stats)

        # Build MatchData
        match_date = datetime.fromisoformat(data['match_date']) if 'match_date' in data else datetime.now()
        match_data = MatchData(
            home_team=home_team,
            away_team=away_team,
            league=league,
            match_date=match_date,
            home_odds=data['home_odds'],
            draw_odds=data['draw_odds'],
            away_odds=data['away_odds'],
            home_form=home_form,
            away_form=away_form,
            home_league_position=realtime_data.get('home_league_position'),
            away_league_position=realtime_data.get('away_league_position'),
            home_injuries=realtime_data.get('home_injuries', []),
            away_injuries=realtime_data.get('away_injuries', []),
            h2h_matches=realtime_data.get('h2h_matches', []),
            referee=realtime_data.get('referee'),
            is_cup_match=data.get('is_cup_match', False),
        )

        # Generate prediction
        prediction_result = predictor_instance.predict(match_data)

        print(f"\nPrediction result:")
        print(f"  Score: {prediction_result.predicted_score}")
        print(f"  Winner: {prediction_result.predicted_winner}")
        print(f"  Home prob: {prediction_result.home_win_probability:.1%}")

        # ========== STEP 3: LLM Deep Analysis ==========
        print("\n" + "="*60)
        print("STEP 3: LLM deep analysis (5-10 seconds)")
        print("="*60)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            llm_analysis = loop.run_until_complete(
                generate_llm_analysis(
                    realtime_data=realtime_data,
                    dimension_scores=prediction_result.dimension_scores,
                    use_zhipu=True,
                    use_minimax=True
                )
            )
        finally:
            loop.close()

        # ========== FINAL: Build Response ==========
        total_elapsed = time.time() - total_start

        print("\n" + "="*60)
        print(f"PREDICTION COMPLETE! Total time: {total_elapsed:.2f}s")
        print("="*60)

        return jsonify({
            # Basic prediction
            'home_team': prediction_result.home_team,
            'away_team': prediction_result.away_team,
            'match_date': prediction_result.match_date.isoformat(),
            'predicted_score': prediction_result.predicted_score,
            'predicted_winner': prediction_result.predicted_winner,
            'home_win_probability': round(prediction_result.home_win_probability, 3),
            'draw_probability': round(prediction_result.draw_probability, 3),
            'away_win_probability': round(prediction_result.away_win_probability, 3),
            'overall_confidence': round(prediction_result.overall_confidence, 3),

            # Nine dimensions
            'dimension_scores': prediction_result.dimension_scores,

            # Insights
            'key_insights': prediction_result.key_insights,
            'risk_factors': prediction_result.risk_factors,

            # Realtime data summary
            'realtime_data_summary': {
                'data_source': realtime_data.get('data_source', 'unknown'),
                'home_injuries_count': len(realtime_data.get('home_injuries', [])),
                'away_injuries_count': len(realtime_data.get('away_injuries', [])),
                'h2h_matches_count': len(realtime_data.get('h2h_matches', [])),
                'lineups_available': bool(realtime_data.get('lineups')),
            },

            # LLM analysis
            'llm_analysis': {
                'zhipu_analysis': llm_analysis.get('zhipu_analysis'),
                'minimax_analysis': llm_analysis.get('minimax_analysis'),
                'combined_insights': llm_analysis.get('combined_insights', []),
            },

            # Bet recommendation
            'recommended_bet': prediction_result.recommended_bet,
            'bet_confidence': round(prediction_result.bet_confidence, 3) if prediction_result.bet_confidence else None,

            # Meta info
            'processing_time': round(total_elapsed, 2),
            'analysis_timestamp': datetime.now().isoformat(),
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in predict_match: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


def _calculate_form_from_stats(stats: Dict) -> List[str]:
    """Calculate form from team statistics"""
    if not stats:
        return []

    wins = stats.get('wins', 0)
    draws = stats.get('draws', 0)
    losses = stats.get('losses', 0)

    total = wins + draws + losses
    if total == 0:
        return []

    form = []
    win_rate = wins / total

    # Generate 5 matches based on win rate
    for i in range(5):
        if win_rate > 0.6:
            form.append('W')
        elif win_rate > 0.4:
            form.append('D')
        else:
            form.append('L')

    return form


@app.route('/api/predict/quick', methods=['POST'])
def predict_quick():
    """
    Quick prediction with minimal data (NO realtime fetching)
    Uses CSV historical data only (~2 seconds)
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Use quick_predict convenience function
        from models.nine_dimensions import quick_predict
        result = quick_predict(
            home_team=data['home_team'],
            away_team=data['away_team'],
            home_odds=data['home_odds'],
            draw_odds=data['draw_odds'],
            away_odds=data['away_odds'],
            league=data.get('league'),
            home_form=data.get('home_form'),
            away_form=data.get('away_form'),
            home_league_position=data.get('home_league_position'),
            away_league_position=data.get('away_league_position'),
            is_cup_match=data.get('is_cup_match', False),
            home_matches_last_14_days=data.get('home_matches_last_14_days', 0),
            away_matches_last_14_days=data.get('away_matches_last_14_days', 0),
        )

        return jsonify({
            'home_team': result.home_team,
            'away_team': result.away_team,
            'predicted_score': result.predicted_score,
            'predicted_winner': result.predicted_winner,
            'home_win_probability': round(result.home_win_probability, 3),
            'draw_probability': round(result.draw_probability, 3),
            'away_win_probability': round(result.away_win_probability, 3),
            'dimension_scores': result.dimension_scores,
            'overall_confidence': round(result.overall_confidence, 3),
            'key_insights': result.key_insights,
            'risk_factors': result.risk_factors,
            'recommended_bet': result.recommended_bet,
            'bet_confidence': round(result.bet_confidence, 3) if result.bet_confidence else None,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PYTHON_ENGINE_PORT', 8002))
    debug = os.getenv('PYTHON_ENGINE_DEBUG', 'False').lower() == 'true'

    print("="*60)
    print("  Football Prediction Engine - Flask Server")
    print("="*60)
    print(f"  Starting on port {port}...")
    print(f"  Debug mode: {debug}")
    print("="*60)

    # Print all registered routes
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.methods} {rule.rule}")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=port, debug=debug)
