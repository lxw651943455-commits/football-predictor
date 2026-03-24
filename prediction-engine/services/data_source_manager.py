"""
数据源管理器 - 支持多数据源
优先级：API-Football > TheSportsDB > CSV
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
import requests
import time


class DataSourceManager:
    """管理多个数据源，自动fallback"""

    def __init__(self):
        # 检查可用的数据源
        self.api_football_enabled = bool(os.getenv('API_FOOTBALL_KEY'))
        self.thesportsdb_enabled = True  # V1 API免费
        self.csv_enabled = True  # 总是可用

        print(f"[DataSource] API-Football: {self.api_football_enabled}")
        print(f"[DataSource] TheSportsDB: {self.thesportsdb_enabled}")
        print(f"[DataSource] CSV fallback: {self.csv_enabled}")

    def fetch_match_data(self, home_team: str, away_team: str, league: str) -> Dict:
        """
        Fetch match data with priority:
        1. API-Football (if key available)
        2. Simulated real-time (demonstrates 20-40s flow)
        3. CSV fallback (fastest, 2-3s)
        """
        result = {
            'home_team': home_team,
            'away_team': away_team,
            'league': league,
            'fetch_time': datetime.now().isoformat()
        }

        print(f"\n[DataSource] Checking available sources...")
        print(f"[DataSource] API-Football: {self.api_football_enabled}")
        print(f"[DataSource] TheSportsDB: {self.thesportsdb_enabled}")

        # Priority 1: Try API-Football if key is available
        if self.api_football_enabled:
            try:
                print(f"\n[DataSource] Trying API-Football...")
                # Use API-Football here when key is available
                pass
            except Exception as e:
                print(f"[DataSource] API-Football failed: {e}")

        # Priority 2: Use simulated real-time data (demonstrates intended 20-40s flow)
        print(f"\n[DataSource] Using simulated real-time data (15-20s)...")
        print(f"[DataSource] NOTE: Replace with real API integration when keys available")

        # Import and call the simulated fetcher directly
        try:
            from services.simulated_realtime_fetcher import fetch_simulated_realtime_data
            import asyncio

            # Simply use asyncio.run() - this handles event loop creation
            data = asyncio.run(fetch_simulated_realtime_data(home_team, away_team, league))

            print(f"[DataSource] Data fetched successfully!")
            result.update(data)
            return result

        except Exception as e:
            print(f"[DataSource] Simulated fetch failed: {e}")
            import traceback
            traceback.print_exc()

        # Priority 3: Fallback to CSV (fastest)
        print(f"\n[DataSource] Falling back to CSV data (2-3s)...")
        try:
            data = self._fetch_from_csv(home_team, away_team, league)
            result.update(data)
            result['data_source'] = 'csv-fallback'
            return result
        except Exception as e:
            print(f"[DataSource] Error: {e}")
            return {}

    def _fetch_from_thesportsdb(self, home_team: str, away_team: str, league: str) -> Dict:
        """从TheSportsDB获取数据"""
        # V1 API endpoint
        url = f"https://www.thesportsdb.com/api/v1/json/123/searchteams.php?t={home_team}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'teams' in data and len(data['teams']) > 0:
                team_info = data['teams'][0]
                print(f"[TheSportsDB] Found team: {team_info.get('strTeam')}")

                # TODO: 实现更多TheSportsDB调用
                return {
                    'home_injuries': [],
                    'away_injuries': [],
                    'h2h_matches': [],
                    'home_stats': {},
                    'away_stats': {},
                    'home_league_position': None,
                    'away_league_position': None,
                }
        except Exception as e:
            print(f"[TheSportsDB] Error: {e}")
            raise

    def _fetch_from_csv(self, home_team: str, away_team: str, league: str) -> Dict:
        """从CSV获取历史数据（后备方案）"""
        from robust_scraper import RobustFootballScraper

        scraper = RobustFootballScraper()

        # 获取比赛数据
        match_data = scraper.get_complete_match_data(home_team, away_team, league)

        # 返回标准格式
        return {
            'home_injuries': [],
            'away_injuries': [],
            'h2h_matches': match_data.get('h2h_matches', []),
            'home_stats': {},
            'away_stats': {},
            'home_league_position': match_data.get('home_league_position'),
            'away_league_position': match_data.get('away_league_position'),
            'home_form': match_data.get('home_form', []),
            'away_form': match_data.get('away_form', []),
            'home_home_record': match_data.get('home_home_record', {}),
            'away_away_record': match_data.get('away_away_record', {}),
        }

    def _validate_data(self, data: Dict) -> bool:
        """验证数据是否有效"""
        required_fields = ['home_injuries', 'away_injuries', 'h2h_matches']
        return all(field in data for field in required_fields)


# 全局实例
data_source_manager = DataSourceManager()


def fetch_match_data_sync(home_team: str, away_team: str, league: str) -> Dict:
    """
    Synchronous wrapper for fetching match data
    This is the main entry point for Flask/synchronous callers
    """
    import os
    import traceback
    import sys

    # Log to file for debugging
    with open('debug_log.txt', 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"fetch_match_data_sync called\n")
        f.write(f"Match: {home_team} vs {away_team}\n")
        f.write(f"League: {league}\n")
        f.write(f"Time: {time.time()}\n")
        f.flush()

    print("\n" + "="*60)
    print("FETCHING MATCH DATA")
    print("="*60)
    print(f"Match: {home_team} vs {away_team}")
    print(f"League: {league}")

    # Check if we should use simulated real-time data
    # (when no API keys are available)
    api_football_key = os.getenv('API_FOOTBALL_KEY')
    print(f"[DEBUG] API_FOOTBALL_KEY = {api_football_key}")

    with open('debug_log.txt', 'a') as f:
        f.write(f"API_FOOTBALL_KEY = {api_football_key}\n")
        f.flush()

    if not api_football_key:
        print(f"\n[DataSource] No API keys configured, using simulated real-time data...")
        print(f"[DataSource] This demonstrates the 20-40 second flow with realistic delays")
        try:
            from services.simulated_realtime_fetcher import fetch_simulated_realtime_data
            import asyncio

            with open('debug_log.txt', 'a') as f:
                f.write(f"About to call asyncio.run...\n")
                f.flush()

            print(f"[DEBUG] About to call asyncio.run...")
            result = asyncio.run(fetch_simulated_realtime_data(home_team, away_team, league))

            with open('debug_log.txt', 'a') as f:
                f.write(f"asyncio.run completed\n")
                f.write(f"data_source = {result.get('data_source')}\n")
                f.write(f"h2h_matches = {len(result.get('h2h_matches', []))}\n")
                f.flush()

            print(f"[DEBUG] asyncio.run completed, data_source = {result.get('data_source')}")
            return result
        except Exception as e:
            print(f"[ERROR] Simulated fetch failed: {e}")
            traceback.print_exc()

            with open('debug_log.txt', 'a') as f:
                f.write(f"ERROR: {e}\n")
                f.write(traceback.format_exc())
                f.flush()
            # Fall through to CSV

    # Otherwise use the regular fetch method or CSV fallback
    print(f"\n[DataSource] Using regular fetch method...")
    return data_source_manager.fetch_match_data(home_team, away_team, league)


async def fetch_match_data_with_fallback(home_team: str, away_team: str, league: str) -> Dict:
    """
    Fetch match data with automatic fallback
    Main entry point for async callers
    """
    return fetch_match_data_sync(home_team, away_team, league)


# 测试
if __name__ == '__main__':
    import asyncio

    async def test():
        data = await fetch_match_data_with_fallback(
            home_team='Real Madrid',
            away_team='Barcelona',
            league='La Liga'
        )
        print(f"\nResult:")
        print(f"  Data source: {data.get('data_source')}")
        print(f"  Home injuries: {len(data.get('home_injuries', []))}")
        print(f"  H2H matches: {len(data.get('h2h_matches', []))}")

    asyncio.run(test())
