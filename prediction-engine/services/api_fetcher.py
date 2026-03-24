"""
API Data Fetcher Service
Aggregates data from The Odds API and API-Football
Implements intelligent caching to optimize API usage
"""

import os
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib


@dataclass
class CacheEntry:
    """Cache entry with expiration"""
    data: Any
    expires_at: datetime
    key: str


class APIFetcher:
    """
    Unified API fetcher for both The Odds API and API-Football
    Implements caching to reduce API calls
    """

    # Cache TTL configurations (in seconds)
    CACHE_TTL = {
        'odds': 300,           # 5 minutes - odds change frequently
        'injuries': 3600,      # 1 hour
        'players': 3600,       # 1 hour
        'h2h': 86400,          # 24 hours - historical data doesn't change
        'team_stats': 86400,   # 24 hours
        'referee': 86400,      # 24 hours
        'predictions': 1800,   # 30 minutes - our calculations
    }

    def __init__(self, odds_api_key: str, football_api_key: str):
        """
        Initialize API fetcher with credentials

        Args:
            odds_api_key: The Odds API key
            football_api_key: API-Football key
        """
        self.odds_api_key = odds_api_key
        self.football_api_key = football_api_key

        self.odds_base_url = "https://api.the-odds-api.com/v4"
        self.football_base_url = "https://v3.football.api-sports.io"

        # In-memory cache (use Redis in production)
        self.cache: Dict[str, CacheEntry] = {}

        # Request rate limiting
        self.last_request_time: Dict[str, float] = {}
        self.min_request_interval = 0.2  # 200ms between requests

    def _generate_cache_key(self, category: str, params: Dict) -> str:
        """Generate cache key from category and parameters"""
        param_str = json.dumps(params, sort_keys=True)
        return f"{category}:{hashlib.md5(param_str.encode()).hexdigest()}"

    def _get_cached(self, category: str, params: Dict) -> Optional[Any]:
        """Get data from cache if valid"""
        key = self._generate_cache_key(category, params)
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry.expires_at:
                return entry.data
            else:
                # Expired, remove from cache
                del self.cache[key]
        return None

    def _set_cached(self, category: str, params: Dict, data: Any):
        """Store data in cache"""
        key = self._generate_cache_key(category, params)
        ttl = self.CACHE_TTL.get(category, 3600)
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = CacheEntry(data=data, expires_at=expires_at, key=key)

    async def _rate_limit(self, api: str):
        """Rate limit requests"""
        now = time.time()
        if api in self.last_request_time:
            elapsed = now - self.last_request_time[api]
            if elapsed < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval - elapsed)
        self.last_request_time[api] = time.time()

    # ========== The Odds API Methods ==========

    async def fetch_odds(
        self,
        sport: str = "soccer",
        regions: str = "eu",
        markets: str = "h2h,ou,ah",
        date_format: str = "iso"
    ) -> List[Dict]:
        """
        Fetch odds from The Odds API

        Args:
            sport: Sport key (default: soccer)
            regions: Regions for odds (eu, uk, us)
            markets: Betting markets (h2h, ou=over/under, ah=asian handicap)
            date_format: Date format

        Returns:
            List of matches with odds
        """
        # Check cache first
        cache_params = {'sport': sport, 'regions': regions, 'markets': markets}
        cached = self._get_cached('odds', cache_params)
        if cached:
            return cached

        await self._rate_limit('odds')

        url = f"{self.odds_base_url}/sports/{sport}/odds"
        params = {
            'apiKey': self.odds_api_key,
            'regions': regions,
            'markets': markets,
            'dateFormat': date_format,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self._set_cached('odds', cache_params, data)
                    return data
                else:
                    error_text = await response.text()
                    raise Exception(f"The Odds API error: {response.status} - {error_text}")

    async def fetch_match_odds(self, match_id: str) -> Dict:
        """Fetch odds for a specific match"""
        # This would use the odds endpoint with match filter
        # Implementation depends on The Odds API v4 structure
        pass

    # ========== API-Football Methods ==========

    async def _football_request(self, endpoint: str, params: Dict) -> Dict:
        """Make request to API-Football with proper headers"""
        await self._rate_limit('football')

        url = f"{self.football_base_url}/{endpoint}"
        headers = {
            'x-rapidapi-key': self.football_api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    raise Exception("API-Football rate limit exceeded")
                else:
                    error_text = await response.text()
                    raise Exception(f"API-Football error: {response.status} - {error_text}")

    async def fetch_injuries(self, team_id: int, league_id: int) -> List[Dict]:
        """
        Fetch injuries and suspensions for a team

        Args:
            team_id: Team ID
            league_id: League ID

        Returns:
            List of injured/suspended players
        """
        cache_params = {'team_id': team_id, 'league_id': league_id}
        cached = self._get_cached('injuries', cache_params)
        if cached:
            return cached

        data = await self._football_request('injuries', {
            'team': team_id,
            'league': league_id,
            'season': self._get_current_season()
        })

        if 'response' in data:
            self._set_cached('injuries', cache_params, data['response'])
            return data['response']
        return []

    async def fetch_lineups(self, fixture_id: int) -> Dict:
        """
        Fetch lineups for a match

        Args:
            fixture_id: Match fixture ID

        Returns:
            Lineup data for both teams
        """
        cache_params = {'fixture_id': fixture_id}
        cached = self._get_cached('players', cache_params)
        if cached:
            return cached

        data = await self._football_request('fixtures/lineups', {
            'fixture': fixture_id
        })

        if 'response' in data:
            self._set_cached('players', cache_params, data['response'])
            return data['response']
        return {}

    async def fetch_head_to_head(
        self,
        home_team_id: int,
        away_team_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch head-to-head history between two teams

        Args:
            home_team_id: Home team ID
            away_team_id: Away team ID
            limit: Number of matches to retrieve

        Returns:
            List of historical matches
        """
        cache_params = {'h2h': f"{home_team_id}-{away_team_id}", 'limit': limit}
        cached = self._get_cached('h2h', cache_params)
        if cached:
            return cached

        data = await self._football_request('fixtures/headtohead', {
            'h2h': f"{home_team_id}-{away_team_id}",
            'last': limit
        })

        if 'response' in data:
            self._set_cached('h2h', cache_params, data['response'])
            return data['response']
        return []

    async def fetch_team_stats(self, team_id: int, league_id: int) -> Dict:
        """
        Fetch team statistics

        Args:
            team_id: Team ID
            league_id: League ID

        Returns:
            Team statistics
        """
        cache_params = {'team_id': team_id, 'league_id': league_id, 'type': 'stats'}
        cached = self._get_cached('team_stats', cache_params)
        if cached:
            return cached

        data = await self._football_request('teams/statistics', {
            'team': team_id,
            'league': league_id,
            'season': self._get_current_season()
        })

        if 'response' in data:
            self._set_cached('team_stats', cache_params, data['response'])
            return data['response']
        return {}

    async def fetch_referee_info(self, referee_id: int) -> Dict:
        """
        Fetch referee statistics

        Args:
            referee_id: Referee ID

        Returns:
            Referee statistics
        """
        cache_params = {'referee_id': referee_id}
        cached = self._get_cached('referee', cache_params)
        if cached:
            return cached

        data = await self._football_request('referees', {
            'id': referee_id
        })

        if 'response' in data and len(data['response']) > 0:
            self._set_cached('referee', cache_params, data['response'][0])
            return data['response'][0]
        return {}

    async def fetch_fixtures(
        self,
        league_id: int,
        date: Optional[str] = None,
        status: str = "NS"
    ) -> List[Dict]:
        """
        Fetch fixtures for a league

        Args:
            league_id: League ID
            date: Date filter (YYYY-MM-DD)
            status: Match status (NS=Not Started, BT=In Play, FT=Finished)

        Returns:
            List of fixtures
        """
        params = {'league': league_id, 'season': self._get_current_season()}
        if date:
            params['date'] = date

        # Fixtures are cached for a shorter time
        cache_params = params.copy()
        cached = self._get_cached('odds', cache_params)
        if cached and date:
            # Only cache if specific date requested
            return cached

        data = await self._football_request('fixtures', params)

        if 'response' in data:
            if date:
                self._set_cached('odds', cache_params, data['response'])
            return data['response']
        return []

    async def fetch_standings(self, league_id: int) -> List[Dict]:
        """
        Fetch league standings

        Args:
            league_id: League ID

        Returns:
            League standings table
        """
        cache_params = {'league_id': league_id, 'type': 'standings'}
        cached = self._get_cached('team_stats', cache_params)
        if cached:
            return cached

        data = await self._football_request('standings', {
            'league': league_id,
            'season': self._get_current_season()
        })

        if 'response' in data and len(data['response']) > 0:
            standings = data['response'][0].get('league', {}).get('standings', [])
            self._set_cached('team_stats', cache_params, standings)
            return standings
        return []

    # ========== Utility Methods ==========

    def _get_current_season(self) -> int:
        """Get current football season (year)"""
        now = datetime.now()
        if now.month >= 8:
            return now.year
        else:
            return now.year - 1

    def clear_cache(self, category: Optional[str] = None):
        """Clear cache (all or specific category)"""
        if category:
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(category)]
            for key in keys_to_remove:
                del self.cache[key]
        else:
            self.cache.clear()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total = len(self.cache)
        by_category = {}
        for key in self.cache.keys():
            category = key.split(':')[0]
            by_category[category] = by_category.get(category, 0) + 1
        return {
            'total_entries': total,
            'by_category': by_category
        }


# Convenience function to create fetcher from environment variables
def create_fetcher_from_env() -> APIFetcher:
    """Create APIFetcher using environment variables"""
    odds_key = os.getenv('THE_ODDS_API_KEY')
    football_key = os.getenv('API_FOOTBALL_KEY')

    if not odds_key:
        raise ValueError("THE_ODDS_API_KEY environment variable not set")
    if not football_key:
        raise ValueError("API_FOOTBALL_KEY environment variable not set")

    return APIFetcher(odds_api_key=odds_key, football_api_key=football_key)


if __name__ == "__main__":
    # Test the fetcher
    async def test():
        import os
        from dotenv import load_dotenv

        load_dotenv()

        fetcher = APIFetcher(
            odds_api_key=os.getenv('THE_ODDS_API_KEY', ''),
            football_api_key=os.getenv('API_FOOTBALL_KEY', '')
        )

        # Test odds fetch
        print("Fetching odds...")
        try:
            odds = await fetcher.fetch_odds()
            print(f"Found {len(odds)} matches with odds")
        except Exception as e:
            print(f"Error: {e}")

        # Test cache stats
        print(f"\nCache stats: {fetcher.get_cache_stats()}")

    asyncio.run(test())
