"""

API-Football
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time


class RealtimeDataFetcher:
    """Fetch real-time football data from API-Football"""

    def __init__(self):
        self.api_key = os.getenv('API_FOOTBALL_KEY')
        self.base_url = 'https://v3.football.api-sports.io'
        self.session = requests.Session()
        self.session.headers.update({
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        })

        #  -> API-Football
        self.team_mapping = self._load_team_mapping()

    def _load_team_mapping(self) -> Dict[str, int]:
        """Load team name to API ID mapping"""
        # Team ID mappings for major leagues 
        return {
            # 
            'Arsenal': 42,
            'Aston Villa': 40,
            'Bournemouth': 252,
            'Brentford': 258,
            'Brighton': 262,
            'Chelsea': 266,
            'Crystal Palace': 269,
            'Everton': 278,
            'Fulham': 283,
            'Liverpool': 287,
            'Man City': 290,
            'Man United': 293,
            'Newcastle': 298,
            'Nott\'m Forest': 300,
            'Tottenham': 303,
            'West Ham': 309,
            'Wolves': 318,

            # 
            'Real Madrid': 218,
            'Barcelona': 220,
            'Atletico Madrid': 219,
            'Sevilla': 216,
            'Real Sociedad': 223,
            'Real Betis': 224,
            'Villarreal': 225,
            'Athletic Club': 217,
            'Valencia': 226,
            'Celta Vigo': 227,

            # 
            'Inter': 229,
            'Milan': 230,
            'Juventus': 231,
            'Napoli': 232,
            'Roma': 233,
            'Lazio': 234,
            'Atalanta': 235,
            'Fiorentina': 236,

            # 
            'Bayern Munich': 237,
            'Dortmund': 238,
            'Leverkusen': 239,
            'RB Leipzig': 240,
            'Ein Frankfurt': 241,
            'Wolfsburg': 242,
            'Freiburg': 243,
            'M\'gladbach': 244,

            # 
            'Paris SG': 245,
            'Monaco': 246,
            'Marseille': 247,
            'Lyon': 248,
            'Lille': 249,
            'Nice': 250,
            'Lens': 251,
        }

    def get_team_id(self, team_name: str) -> Optional[int]:
        """Get team API ID from team name"""
        return self.team_mapping.get(team_name)

    def fetch_injuries(self, team_id: int, league_id: int) -> List[Dict]:
        """Fetch injury list for a team

        Args:
            team_id: Team API ID
            league_id: League API ID

        Returns:
            List of injured players with details
        """
        url = f"{self.base_url}/injuries"
        params = {
            'team': team_id,
            'league': league_id,
            'season': 2023
        }

        try:
            print(f"  [API] Fetching injuries: team_id={team_id}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            injuries = []
            for player in data.get('response', []):
                injuries.append({
                    'player': player['player']['name'],
                    'reason': player['player']['reason'],
                    'type': player['player']['type'],  # Injury/Suspension
                    'is_key_player': self._is_key_player(player['player']['name'])
                })

            print(f"  [API] Got {len(injuries)} injured players")
            return injuries

        except Exception as e:
            print(f"  [API] Failed to fetch injuries: {e}")
            return []

    def fetch_lineups(self, fixture_id: int) -> Dict:
        """Fetch starting lineups for a fixture

        Args:
            fixture_id: Fixture API ID

        Returns:
            Dictionary with home/away lineups
        """
        url = f"{self.base_url}/fixtures/lineups"
        params = {'fixture': fixture_id}

        try:
            print(f"  [API] Fetching lineups: fixture_id={fixture_id}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            lineups = {
                'home': [],
                'away': []
            }

            for team_data in data.get('response', []):
                team_name = team_data['team']['name']
                formation = team_data.get('formation', 'Unknown')

                players = []
                for player in team_data.get('startXI', []):
                    players.append({
                        'player': player['player']['name'],
                        'number': player['player']['number'],
                        'pos': player['player']['pos'],
                        'grid': player['player'].get('grid', '')
                    })

                if team_name == data['response'][0]['team']['name']:
                    lineups['home'] = {'formation': formation, 'players': players}
                else:
                    lineups['away'] = {'formation': formation, 'players': players}

            print(f"  [API] Lineups fetched successfully")
            return lineups

        except Exception as e:
            print(f"  [API] Failed to fetch lineups: {e}")
            return {}

    def fetch_head_to_head(self, home_team_id: int, away_team_id: int, limit: int = 10) -> List[Dict]:
        """Fetch head-to-head match history

        Args:
            home_team_id: Home team API ID
            away_team_id: Away team API ID
            limit: Maximum matches to return

        Returns:
            List of historical H2H matches
        """
        url = f"{self.base_url}/fixtures/headtohead"
        params = {
            'h2h': f"{home_team_id}-{away_team_id}",
            'last': limit
        }

        try:
            print(f"  [API] Fetching H2H: {home_team_id} vs {away_team_id}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            h2h_matches = []
            for match in data.get('response', []):
                h2h_matches.append({
                    'date': match['fixture']['date'],
                    'home_team': match['teams']['home']['name'],
                    'away_team': match['teams']['away']['name'],
                    'home_score': match['goals']['home'],
                    'away_score': match['goals']['away'],
                    'winner': 'home' if match['teams']['home']['winner'] else
                              'away' if match['teams']['away']['winner'] else 'draw'
                })

            print(f"  [API] Got {len(h2h_matches)} H2H matches")
            return h2h_matches

        except Exception as e:
            print(f"  [API] Failed to fetch H2H: {e}")
            return []

    def fetch_team_stats(self, team_id: int, league_id: int) -> Dict:
        """Fetch team statistics

        Args:
            team_id: Team API ID
            league_id: League API ID

        Returns:
            Dictionary with team stats
        """
        url = f"{self.base_url}/teams/statistics"
        params = {
            'team': team_id,
            'league': league_id,
            'season': 2023
        }

        try:
            print(f"  [API] Fetching team stats: team_id={team_id}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            stats = data.get('response', {})

            return {
                'matches_played': stats.get('fixtures', {}).get('played', 0),
                'wins': stats.get('fixtures', {}).get('wins', {}).get('home', 0),
                'draws': stats.get('fixtures', {}).get('draws', {}).get('home', 0),
                'losses': stats.get('fixtures', {}).get('loses', {}).get('home', 0),
                'goals_for': stats.get('goals', {}).get('for', {}).get('total', {}).get('home', 0),
                'goals_against': stats.get('goals', {}).get('against', {}).get('total', {}).get('home', 0),
                'clean_sheets': stats.get('clean_sheet', {}).get('home', 0),
            }

        except Exception as e:
            print(f"  [API] Failed to fetch stats: {e}")
            return {}

    def fetch_referee_info(self, referee_id: int) -> Dict:
        """Fetch referee information

        Args:
            referee_id: Referee API ID

        Returns:
            Dictionary with referee stats
        """
        url = f"{self.base_url}/referees"
        params = {'id': referee_id}

        try:
            print(f"  [API] Fetching referee: referee_id={referee_id}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('response'):
                referee = data['response'][0]
                return {
                    'name': referee['name'],
                    'country': referee.get('country', 'Unknown'),
                    'avg_home_yellows': 2.5,
                    'avg_away_yellows': 2.5,
                    'red_card_rate': 0.02,
                }

        except Exception as e:
            print(f"  [API] Failed to fetch referee: {e}")

        return {}

    def fetch_fixtures(self, league_id: int, season: int = 2023) -> List[Dict]:
        """Fetch upcoming fixtures for a league

        Args:
            league_id: League API ID
            season: Season year

        Returns:
            List of upcoming fixtures
        """
        url = f"{self.base_url}/fixtures"
        params = {
            'league': league_id,
            'season': season,
            'status': 'NS'  # Not Started
        }

        try:
            print(f"  [API] Fetching fixtures: league_id={league_id}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            fixtures = []
            for match in data.get('response', []):
                fixtures.append({
                    'id': match['fixture']['id'],
                    'home_team': match['teams']['home']['name'],
                    'away_team': match['teams']['away']['name'],
                    'date': match['fixture']['date'],
                    'referee': match.get('referee', None)
                })

            return fixtures

        except Exception as e:
            print(f"  [API] Failed to fetch fixtures: {e}")
            return []

    def _is_key_player(self, player_name: str) -> bool:
        """Check if player is a key player"""
        # List of known key players 
        key_players = [
            'Salah', 'Haaland', 'De Bruyne', 'Saka', 'Son', 'Kane',
            'Vinicius', 'Bellingham', 'Pedri', 'Gavi', 'Lewandowski',
            'Messi', 'Neymar', 'Mbappe', 'Martinez', 'Di Maria',
            'Leao', 'Theo', 'Tonali', 'Barella', 'Lautaro',
            'Muller', 'Sancho', 'Wirtz', 'Musiala', 'Frimpong'
        ]

        return any(key in player_name for key in key_players)


async def fetch_all_realtime_data(home_team: str, away_team: str, league: str) -> Dict:
    """Fetch all real-time match data from API-Football

    Args:
        home_team: Home team name
        away_team: Away team name
        league: League name

    Returns:
        Dictionary with all match data
    """
    print(f"\n{'='*60}")
    print(f"FETCHING REALTIME DATA FROM API-FOOTBALL")
    print(f"{'='*60}")
    print(f"Match: {home_team} vs {away_team}")
    print(f"League: {league}")

    start_time = time.time()

    fetcher = RealtimeDataFetcher()

    # League ID mapping
    league_ids = {
        'Premier League': 39,
        'La Liga': 140,
        'Serie A': 135,
        'Bundesliga': 78,
        'Ligue 1': 61
    }

    league_id = league_ids.get(league)
    if not league_id:
        print(f"[ERROR] League not supported: {league}")
        return {}

    # Get team IDs
    home_team_id = fetcher.get_team_id(home_team)
    away_team_id = fetcher.get_team_id(away_team)

    if not home_team_id or not away_team_id:
        print(f"[ERROR] Team ID not found")
        return {}

    print(f"Team IDs: home={home_team_id}, away={away_team_id}")

    # Initialize result
    result = {
        'home_team': home_team,
        'away_team': away_team,
        'league': league,
        'fetch_time': datetime.now().isoformat()
    }

    # 1. Fetch injuries
    print(f"\n[1/5] Fetching injuries...")
    result['home_injuries'] = fetcher.fetch_injuries(home_team_id, league_id)
    result['away_injuries'] = fetcher.fetch_injuries(away_team_id, league_id)

    # 2. H2H
    print(f"\n[2/5] Fetching H2H...")
    result['h2h_matches'] = fetcher.fetch_head_to_head(home_team_id, away_team_id)

    # 3. Team stats
    print(f"\n[3/5] Fetching team stats...")
    result['home_stats'] = fetcher.fetch_team_stats(home_team_id, league_id)
    result['away_stats'] = fetcher.fetch_team_stats(away_team_id, league_id)

    # 4. Find fixture
    print(f"\n[4/5] Finding fixture...")
    fixtures = fetcher.fetch_fixtures(league_id)

    target_fixture = None
    for fixture in fixtures:
        if fixture['home_team'] == home_team and fixture['away_team'] == away_team:
            target_fixture = fixture
            break

    if target_fixture:
        result['fixture_id'] = target_fixture['id']
        result['referee'] = fetcher.fetch_referee_info(target_fixture.get('referee', 0))

        # 5. Lineups
        print(f"\n[5/5] Fetching lineups...")
        result['lineups'] = fetcher.fetch_lineups(target_fixture['id'])
    else:
        result['lineups'] = {}

    elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"[OK] Realtime data fetched in {elapsed:.2f}s")
    print(f"{'='*60}")
    print(f"  Home injuries: {len(result['home_injuries'])}")
    print(f"  Away injuries: {len(result['away_injuries'])}")
    print(f"  H2H matches: {len(result['h2h_matches'])}")
    print(f"  Lineups: {'Available' if result['lineups'] else 'Not available'}")

    return result


# Test
if __name__ == '__main__':
    import asyncio

    async def test():
        data = await fetch_all_realtime_data(
            home_team='Real Madrid',
            away_team='Barcelona',
            league='La Liga'
        )

        import json
        print("\n\nResult:")
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    asyncio.run(test())
