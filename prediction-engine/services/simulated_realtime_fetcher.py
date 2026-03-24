"""
Simulated Real-Time Data Fetcher
Demonstrates the 20-40 second prediction flow with realistic delays

This simulates real-time API calls to show the intended workflow.
Replace these simulated calls with actual API integrations when API keys are available.
"""

import random
import time
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta


class SimulatedRealtimeFetcher:
    """Simulate real-time data fetching with realistic delays"""

    def __init__(self):
        # Team reputation data (for realistic predictions)
        self.team_strength = {
            # La Liga
            'Real Madrid': 88, 'Barcelona': 87, 'Atletico Madrid': 84,
            'Sevilla': 80, 'Real Sociedad': 79,

            # Premier League
            'Man City': 89, 'Arsenal': 87, 'Liverpool': 86,
            'Man United': 82, 'Chelsea': 83, 'Tottenham': 81,
            'Newcastle': 80, 'Brighton': 79,

            # Serie A
            'Inter': 85, 'Milan': 84, 'Juventus': 83,
            'Napoli': 84, 'Roma': 81, 'Lazio': 80,

            # Bundesliga
            'Bayern Munich': 88, 'Dortmund': 84, 'Leverkusen': 85,
            'RB Leipzig': 82, 'Ein Frankfurt': 79,

            # Ligue 1
            'Paris SG': 87, 'Monaco': 80, 'Marseille': 79,
        }

        # Real injury examples (periodically updated)
        self.known_injuries = {
            'Real Madrid': ['Courtois', 'Alaba'],
            'Barcelona': [],
            'Man City': ['De Bruyne'],
            'Liverpool': [],
        }

    async def fetch_injuries(self, team_name: str) -> List[Dict]:
        """Simulate fetching injury data from API"""
        print(f"  [Simulated API] Fetching injuries for {team_name}...")
        await asyncio.sleep(random.uniform(2, 4))  # 2-4 second delay

        # Get known injuries or generate random ones
        injuries = []
        known = self.known_injuries.get(team_name, [])

        if known:
            for player in known:
                injuries.append({
                    'player': player,
                    'reason': 'Injury',
                    'type': 'Injury',
                    'is_key_player': self._is_key_player(player)
                })
        else:
            # 30% chance of random injury
            if random.random() < 0.3:
                injuries.append({
                    'player': 'Key Player',
                    'reason': 'Muscle injury',
                    'type': 'Injury',
                    'is_key_player': True
                })

        print(f"  [Simulated API] Got {len(injuries)} injured players")
        return injuries

    async def fetch_h2h(self, home_team: str, away_team: str) -> List[Dict]:
        """Simulate fetching H2H data from API"""
        print(f"  [Simulated API] Fetching H2H for {home_team} vs {away_team}...")
        await asyncio.sleep(random.uniform(3, 5))  # 3-5 second delay

        # Generate realistic H2H data
        h2h_matches = []
        home_strength = self.team_strength.get(home_team, 75)
        away_strength = self.team_strength.get(away_team, 75)

        for i in range(10):
            date = datetime.now() - timedelta(days=random.randint(10, 365) * i)

            # Simulate match result based on team strength
            if home_strength > away_strength + 5:
                home_win_prob = 0.6
            elif away_strength > home_strength + 5:
                home_win_prob = 0.4
            else:
                home_win_prob = 0.5

            rand = random.random()
            if rand < home_win_prob:
                winner = 'home'
                home_score = random.randint(2, 4)
                away_score = random.randint(0, 2)
            elif rand < home_win_prob + 0.25:
                winner = 'draw'
                home_score = random.randint(1, 2)
                away_score = home_score
            else:
                winner = 'away'
                home_score = random.randint(0, 2)
                away_score = random.randint(2, 4)

            h2h_matches.append({
                'date': date.isoformat(),
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'winner': winner
            })

        print(f"  [Simulated API] Got {len(h2h_matches)} H2H matches")
        return h2h_matches

    async def fetch_team_form(self, team_name: str) -> List[str]:
        """Simulate fetching recent form from API"""
        print(f"  [Simulated API] Fetching form for {team_name}...")
        await asyncio.sleep(random.uniform(2, 3))  # 2-3 second delay

        strength = self.team_strength.get(team_name, 75)
        form = []

        # Generate form based on team strength
        for i in range(5):
            if strength > 85:
                prob = {'W': 0.6, 'D': 0.25, 'L': 0.15}
            elif strength > 80:
                prob = {'W': 0.5, 'D': 0.3, 'L': 0.2}
            else:
                prob = {'W': 0.3, 'D': 0.3, 'L': 0.4}

            rand = random.random()
            if rand < prob['W']:
                form.append('W')
            elif rand < prob['W'] + prob['D']:
                form.append('D')
            else:
                form.append('L')

        print(f"  [Simulated API] Form: {form}")
        return form

    async def fetch_standings(self, team_name: str, league: str) -> int:
        """Simulate fetching league position from API"""
        print(f"  [Simulated API] Fetching standings for {team_name}...")
        await asyncio.sleep(random.uniform(1, 2))  # 1-2 second delay

        strength = self.team_strength.get(team_name, 75)
        # Simulate position based on strength
        position = max(1, int(20 - (strength - 70) * 2))

        print(f"  [Simulated API] Position: {position}")
        return position

    async def fetch_lineups(self, home_team: str, away_team: str) -> Dict:
        """Simulate fetching expected lineups from API"""
        print(f"  [Simulated API] Fetching lineups...")
        await asyncio.sleep(random.uniform(2, 3))  # 2-3 second delay

        # 50% chance lineups are available (not announced yet)
        if random.random() < 0.5:
            print(f"  [Simulated API] Lineups not announced yet")
            return {}

        formations = ['4-3-3', '4-2-3-1', '3-5-2', '4-4-2']

        return {
            'home': {
                'formation': random.choice(formations),
                'players': [
                    {'player': 'GK', 'number': 1, 'pos': 'G'},
                    {'player': 'LB', 'number': 3, 'pos': 'D'},
                    {'player': 'CB1', 'number': 4, 'pos': 'D'},
                    {'player': 'CB2', 'number': 5, 'pos': 'D'},
                    {'player': 'RB', 'number': 2, 'pos': 'D'},
                    {'player': 'CM1', 'number': 6, 'pos': 'M'},
                    {'player': 'CM2', 'number': 8, 'pos': 'M'},
                    {'player': 'CM3', 'number': 10, 'pos': 'M'},
                    {'player': 'LW', 'number': 7, 'pos': 'F'},
                    {'player': 'ST', 'number': 9, 'pos': 'F'},
                    {'player': 'RW', 'number': 11, 'pos': 'F'},
                ]
            },
            'away': {
                'formation': random.choice(formations),
                'players': [
                    {'player': 'GK', 'number': 1, 'pos': 'G'},
                    {'player': 'LB', 'number': 3, 'pos': 'D'},
                    {'player': 'CB1', 'number': 4, 'pos': 'D'},
                    {'player': 'CB2', 'number': 5, 'pos': 'D'},
                    {'player': 'RB', 'number': 2, 'pos': 'D'},
                    {'player': 'CM1', 'number': 6, 'pos': 'M'},
                    {'player': 'CM2', 'number': 8, 'pos': 'M'},
                    {'player': 'CM3', 'number': 10, 'pos': 'M'},
                    {'player': 'LW', 'number': 7, 'pos': 'F'},
                    {'player': 'ST', 'number': 9, 'pos': 'F'},
                    {'player': 'RW', 'number': 11, 'pos': 'F'},
                ]
            }
        }

    def _is_key_player(self, player_name: str) -> bool:
        """Check if player is considered a key player"""
        key_players = [
            'Courtois', 'De Bruyne', 'Salah', 'Haaland', 'Vinicius',
            'Bellingham', 'Pedri', 'Gavi', 'Lewandowski', 'Messi',
            'Mbappe', 'Kane', 'Son', 'Saka', 'Alaba'
        ]
        return any(key in player_name for key in key_players)


async def fetch_simulated_realtime_data(home_team: str, away_team: str, league: str) -> Dict:
    """
    Fetch simulated real-time data (demonstrates 20-40 second flow)

    This function simulates the behavior of real API calls.
    Replace with actual API integrations when keys are available.

    Args:
        home_team: Home team name
        away_team: Away team name
        league: League name

    Returns:
        Dictionary with all match data
    """
    print(f"\n{'='*60}")
    print(f"FETCHING REALTIME DATA (SIMULATED)")
    print(f"{'='*60}")
    print(f"Match: {home_team} vs {away_team}")
    print(f"League: {league}")
    print(f"NOTE: This is simulated data. Integrate real APIs when available.")
    print(f"{'='*60}")

    start_time = time.time()

    fetcher = SimulatedRealtimeFetcher()

    # Initialize result
    result = {
        'home_team': home_team,
        'away_team': away_team,
        'league': league,
        'data_source': 'simulated-realtime',
        'fetch_time': datetime.now().isoformat()
    }

    # Step 1: Fetch injuries (2-4 seconds)
    print(f"\n[1/6] Fetching injuries...")
    result['home_injuries'] = await fetcher.fetch_injuries(home_team)
    result['away_injuries'] = await fetcher.fetch_injuries(away_team)

    # Step 2: Fetch H2H (3-5 seconds)
    print(f"\n[2/6] Fetching head-to-head history...")
    result['h2h_matches'] = await fetcher.fetch_h2h(home_team, away_team)

    # Step 3: Fetch form (2-3 seconds)
    print(f"\n[3/6] Fetching recent form...")
    result['home_form'] = await fetcher.fetch_team_form(home_team)
    result['away_form'] = await fetcher.fetch_team_form(away_team)

    # Step 4: Fetch standings (1-2 seconds)
    print(f"\n[4/6] Fetching league standings...")
    result['home_league_position'] = await fetcher.fetch_standings(home_team, league)
    result['away_league_position'] = await fetcher.fetch_standings(away_team, league)

    # Step 5: Fetch team stats (simulated) (2-3 seconds)
    print(f"\n[5/6] Fetching team statistics...")
    await asyncio.sleep(random.uniform(2, 3))
    result['home_stats'] = {
        'matches_played': random.randint(20, 30),
        'wins': random.randint(10, 20),
        'draws': random.randint(3, 8),
        'losses': random.randint(2, 6)
    }
    result['away_stats'] = {
        'matches_played': random.randint(20, 30),
        'wins': random.randint(10, 20),
        'draws': random.randint(3, 8),
        'losses': random.randint(2, 6)
    }
    print(f"  [Simulated API] Got team stats")

    # Step 6: Fetch lineups (2-3 seconds)
    print(f"\n[6/6] Fetching expected lineups...")
    result['lineups'] = await fetcher.fetch_lineups(home_team, away_team)

    elapsed = time.time() - start_time

    print(f"\n{'='*60}")
    print(f"[OK] Realtime data fetched in {elapsed:.2f}s")
    print(f"{'='*60}")
    print(f"  Home injuries: {len(result['home_injuries'])}")
    print(f"  Away injuries: {len(result['away_injuries'])}")
    print(f"  H2H matches: {len(result['h2h_matches'])}")
    print(f"  Home form: {result['home_form']}")
    print(f"  Away form: {result['away_form']}")
    print(f"  Home position: {result['home_league_position']}")
    print(f"  Away position: {result['away_league_position']}")
    print(f"  Lineups: {'Available' if result['lineups'] else 'Not available'}")

    return result


# Test
if __name__ == '__main__':
    import asyncio

    async def test():
        data = await fetch_simulated_realtime_data(
            home_team='Real Madrid',
            away_team='Barcelona',
            league='La Liga'
        )

        print(f"\n\nTotal time: ~15-20 seconds as expected!")
        print(f"Data source: {data['data_source']}")

    asyncio.run(test())
