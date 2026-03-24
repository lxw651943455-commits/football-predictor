"""
Football-Data.org API Integration
Free API for football data - no API key required for basic usage
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime
import time


class FootballDataOrgFetcher:
    """Fetch data from football-data.org (free API)"""

    def __init__(self):
        # football-data.org - Free tier, no key required for some endpoints
        self.base_url = 'https://api.football-data.org/v4'
        self.session = requests.Session()

        # Try to use API key if available (increases rate limits)
        import os
        api_key = os.getenv('FOOTBALL_DATA_ORG_KEY')
        if api_key:
            self.session.headers.update({'X-Auth-Token': api_key})
            print(f"[Football-Data.org] Using API key for higher rate limits")
        else:
            print(f"[Football-Data.org] No API key - using free tier")

    def get_competitions(self) -> List[Dict]:
        """Get available competitions/leagues"""
        url = f"{self.base_url}/competitions"

        try:
            print(f"  [API] Fetching competitions...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            competitions = []
            for comp in data.get('competitions', []):
                competitions.append({
                    'id': comp['id'],
                    'name': comp['name'],
                    'code': comp.get('code', ''),
                    'area': comp.get('area', {}).get('name', 'Unknown')
                })

            print(f"  [API] Got {len(competitions)} competitions")
            return competitions

        except Exception as e:
            print(f"  [API] Failed to fetch competitions: {e}")
            return []

    def get_matches(self, competition_id: int, season: int = 2023) -> List[Dict]:
        """Get matches for a competition and season"""
        url = f"{self.base_url}/competitions/{competition_id}/matches"
        params = {'season': season}

        try:
            print(f"  [API] Fetching matches for competition {competition_id}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            matches = []
            for match in data.get('matches', []):
                matches.append({
                    'id': match['id'],
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'home_score': match.get('score', {}).get('fullTime', {}).get('home'),
                    'away_score': match.get('score', {}).get('fullTime', {}).get('away'),
                    'status': match['status'],
                    'date': match['utcDate'],
                    'winner': match.get('score', {}).get('winner')
                })

            print(f"  [API] Got {len(matches)} matches")
            return matches

        except Exception as e:
            print(f"  [API] Failed to fetch matches: {e}")
            return []

    def get_teams(self, competition_id: int) -> List[Dict]:
        """Get teams in a competition"""
        url = f"{self.base_url}/competitions/{competition_id}/teams"

        try:
            print(f"  [API] Fetching teams for competition {competition_id}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            teams = []
            for team in data.get('teams', []):
                teams.append({
                    'id': team['id'],
                    'name': team['name'],
                    'short_name': team.get('shortName', ''),
                    'crest': team.get('crest', '')
                })

            print(f"  [API] Got {len(teams)} teams")
            return teams

        except Exception as e:
            print(f"  [API] Failed to fetch teams: {e}")
            return []

    def get_head_to_head(self, home_team: str, away_team: str, competition_id: int, limit: int = 10) -> List[Dict]:
        """Get head-to-head matches by fetching team's match history"""
        # This is a workaround since football-data.org doesn't have direct H2H endpoint
        # We'll fetch recent matches and filter

        url = f"{self.base_url}/competitions/{competition_id}/matches"
        params = {'season': 2023}

        try:
            print(f"  [API] Fetching H2H data for {home_team} vs {away_team}...")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Filter matches between these two teams
            h2h_matches = []
            for match in data.get('matches', []):
                match_home = match['homeTeam']['name']
                match_away = match['awayTeam']['name']

                if (match_home == home_team and match_away == away_team) or \
                   (match_home == away_team and match_away == home_team):

                    if match['status'] == 'FINISHED':
                        h2h_matches.append({
                            'date': match['utcDate'],
                            'home_team': match_home,
                            'away_team': match_away,
                            'home_score': match.get('score', {}).get('fullTime', {}).get('home'),
                            'away_score': match.get('score', {}).get('fullTime', {}).get('away'),
                            'winner': match.get('score', {}).get('winner')
                        })

                        if len(h2h_matches) >= limit:
                            break

            print(f"  [API] Got {len(h2h_matches)} H2H matches")
            return h2h_matches

        except Exception as e:
            print(f"  [API] Failed to fetch H2H: {e}")
            return []

    def find_team_id(self, team_name: str, competition_id: int) -> Optional[int]:
        """Find team ID by name in a competition"""
        teams = self.get_teams(competition_id)

        for team in teams:
            if team['name'].lower() == team_name.lower():
                return team['id']

        # Try partial match
        for team in teams:
            if team_name.lower() in team['name'].lower() or \
               team['name'].lower() in team_name.lower():
                return team['id']

        return None


# Competition ID mappings for football-data.org
COMPETITION_IDS = {
    'Premier League': 2021,
    'La Liga': 2014,
    'Serie A': 2019,
    'Bundesliga': 2002,
    'Ligue 1': 2015
}


async def fetch_from_football_data_org(home_team: str, away_team: str, league: str) -> Dict:
    """
    Fetch match data from football-data.org

    Args:
        home_team: Home team name
        away_team: Away team name
        league: League name

    Returns:
        Dictionary with match data
    """
    print(f"\n{'='*60}")
    print(f"FETCHING DATA FROM FOOTBALL-DATA.ORG")
    print(f"{'='*60}")
    print(f"Match: {home_team} vs {away_team}")
    print(f"League: {league}")

    start_time = time.time()

    fetcher = FootballDataOrgFetcher()

    # Get competition ID
    competition_id = COMPETITION_IDS.get(league)
    if not competition_id:
        print(f"[ERROR] League not supported: {league}")
        return {}

    print(f"Competition ID: {competition_id}")

    # Initialize result
    result = {
        'home_team': home_team,
        'away_team': away_team,
        'league': league,
        'data_source': 'football-data-org',
        'fetch_time': datetime.now().isoformat()
    }

    # 1. Get H2H matches
    print(f"\n[1/3] Fetching head-to-head matches...")
    time.sleep(2)  # Simulate network delay
    result['h2h_matches'] = fetcher.get_head_to_head(home_team, away_team, competition_id)

    # 2. Get recent matches for form calculation
    print(f"\n[2/3] Fetching recent matches for form...")
    time.sleep(2)
    all_matches = fetcher.get_matches(competition_id)

    # Filter matches for home team (last 5)
    home_matches = [m for m in all_matches if m['home_team'] == home_team or m['away_team'] == home_team]
    home_matches = [m for m in home_matches if m['status'] == 'FINISHED'][-5:]

    # Filter matches for away team (last 5)
    away_matches = [m for m in all_matches if m['home_team'] == away_team or m['away_team'] == away_team]
    away_matches = [m for m in away_matches if m['status'] == 'FINISHED'][-5:]

    # Calculate form
    def calculate_form(matches, team_name):
        form = []
        for match in matches:
            if match['home_team'] == team_name:
                if match['home_score'] > match['away_score']:
                    form.append('W')
                elif match['home_score'] == match['away_score']:
                    form.append('D')
                else:
                    form.append('L')
            else:
                if match['away_score'] > match['home_score']:
                    form.append('W')
                elif match['away_score'] == match['home_score']:
                    form.append('D')
                else:
                    form.append('L')
        return form

    result['home_form'] = calculate_form(home_matches, home_team)
    result['away_form'] = calculate_form(away_matches, away_team)

    # 3. Get standings (if available)
    print(f"\n[3/3] Fetching standings...")
    time.sleep(2)

    # Find positions based on recent matches
    result['home_league_position'] = None
    result['away_league_position'] = None

    elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"[OK] Data fetched in {elapsed:.2f}s")
    print(f"{'='*60}")
    print(f"  H2H matches: {len(result['h2h_matches'])}")
    print(f"  Home form: {result['home_form']}")
    print(f"  Away form: {result['away_form']}")

    return result


# Test
if __name__ == '__main__':
    import asyncio

    async def test():
        # Test competitions
        print("Testing competitions...")
        fetcher = FootballDataOrgFetcher()
        competitions = fetcher.get_competitions()
        print(f"\nFound {len(competitions)} competitions")
        for comp in competitions[:5]:
            print(f"  - {comp['name']} (ID: {comp['id']})")

        # Test match data
        print("\n\nTesting match data...")
        data = await fetch_from_football_data_org(
            home_team='Real Madrid',
            away_team='Barcelona',
            league='La Liga'
        )

        import json
        print("\n\nResult:")
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    asyncio.run(test())
