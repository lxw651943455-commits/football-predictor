"""
混合API获取器 - 结合betminer和API-Football
betminer: odds, form, probabilities, edge analysis
API-Football: standings, injuries, H2H, team stats, referee
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from functools import lru_cache
import os
from pathlib import Path

# 加载 .env 文件
def load_env():
    """手动加载.env文件"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()


class HybridAPIFetcher:
    """混合API获取器"""

    def __init__(self):
        # RapidAPI key
        self.api_key = os.getenv('API_FOOTBALL_KEY')

        # betminer API
        self.betminer_base = "https://betminer.p.rapidapi.com"
        self.betminer_headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'betminer.p.rapidapi.com'
        }

        # API-Football
        self.football_base = "https://v3.football.api-sports.io"
        self.football_headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }

        # Cache with TTL (5 minutes)
        self.cache = {}
        self.cache_ttl = 300  # seconds

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """从缓存获取数据"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now().timestamp() - timestamp < self.cache_ttl:
                return data
            else:
                del self.cache[key]
        return None

    def _save_to_cache(self, key: str, data: Dict):
        """保存数据到缓存"""
        self.cache[key] = (data, datetime.now().timestamp())

    async def fetch_betminer_edge_analysis(self, date: str) -> List[Dict]:
        """
        获取betminer edge analysis数据
        包含: odds, form, probabilities, edge_analysis
        """
        cache_key = f"betminer_{date}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('data', [])

        url = f"{self.betminer_base}/bm/v3/edge-analysis/{date}"

        try:
            # 过滤掉None值的headers
            headers = {k: v for k, v in self.betminer_headers.items() if v is not None}
            timeout = aiohttp.ClientTimeout(total=60)  # 增加到60秒
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    print(f"[DEBUG] Response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"[DEBUG] Response success: {data.get('success')}")
                        print(f"[DEBUG] Data length: {len(data.get('data', []))}")
                        if data.get('success'):
                            self._save_to_cache(cache_key, data)
                            return data.get('data', [])
                    else:
                        print(f"[DEBUG] Non-200 status: {response.status}")
                        text = await response.text()
                        print(f"[DEBUG] Response: {text[:200]}")
        except Exception as e:
            print(f"[ERROR] Exception fetching betminer data: {e}")
            import traceback
            traceback.print_exc()

        return []

    async def fetch_standings(self, league_id: int) -> List[Dict]:
        """获取联赛积分榜 (API-Football)"""
        cache_key = f"standings_{league_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('data', [])

        url = f"{self.football_base}/v3/standings"
        params = {'league': league_id, 'season': 2024}

        try:
            headers = {k: v for k, v in self.football_headers.items() if v is not None}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers,
                                     params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('response', [])
                        self._save_to_cache(cache_key, {'data': results})
                        return results
        except Exception as e:
            print(f"Error fetching standings: {e}")

        return []

    async def fetch_injuries(self, team_id: int, league_id: int) -> List[Dict]:
        """获取球队伤停 (API-Football)"""
        cache_key = f"injuries_{team_id}_{league_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('data', [])

        # API-Football没有专门的injuries端点，需要从fixtures获取
        # 使用sideline端点
        url = f"{self.football_base}/v3/fixtures/sidelines"
        params = {'league': league_id, 'team': team_id, 'season': 2024}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.football_headers,
                                     params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('response', [])
                        self._save_to_cache(cache_key, {'data': results})
                        return results
        except Exception as e:
            print(f"Error fetching injuries: {e}")

        return []

    async def fetch_head_to_head(self, home_team_id: int, away_team_id: int,
                                  limit: int = 10) -> List[Dict]:
        """获取历史交锋 (API-Football)"""
        cache_key = f"h2h_{home_team_id}_{away_team_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('data', [])

        url = f"{self.football_base}/v3/fixtures/headtohead"
        params = {
            'h2h': f"{home_team_id}-{away_team_id}",
            'last': limit
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.football_headers,
                                     params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get('response', [])
                        self._save_to_cache(cache_key, {'data': results})
                        return results
        except Exception as e:
            print(f"Error fetching H2H: {e}")

        return []

    async def fetch_team_stats(self, team_id: int, league_id: int) -> Optional[Dict]:
        """获取球队统计 (API-Football)"""
        cache_key = f"stats_{team_id}_{league_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('data')

        url = f"{self.football_base}/v3/teams/statistics"
        params = {'league': league_id, 'season': 2024, 'team': team_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.football_headers,
                                     params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('response', {})
                        self._save_to_cache(cache_key, {'data': result})
                        return result
        except Exception as e:
            print(f"Error fetching team stats: {e}")

        return None

    async def fetch_referee_stats(self, referee_id: int) -> Optional[Dict]:
        """获取裁判统计 (API-Football)"""
        cache_key = f"referee_{referee_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached.get('data')

        url = f"{self.football_base}/v3/referees"
        params = {'id': referee_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.football_headers,
                                     params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get('response', {})
                        self._save_to_cache(cache_key, {'data': result})
                        return result
        except Exception as e:
            print(f"Error fetching referee stats: {e}")

        return None

    async def fetch_complete_match_data(self, home_team: str, away_team: str,
                                         league: str, match_date: str) -> Dict:
        """
        获取完整的比赛数据（结合betminer和API-Football）
        返回九维预测所需的所有数据
        """
        # 1. 获取betminer edge analysis
        date_obj = datetime.fromisoformat(match_date).date()
        date_str = date_obj.isoformat()

        betminer_data = await self.fetch_betminer_edge_analysis(date_str)

        # 查找对应比赛
        target_match = None
        for match in betminer_data:
            if (home_team.lower() in match['home_team']['name'].lower() and
                away_team.lower() in match['away_team']['name'].lower()):
                target_match = match
                break

        if not target_match:
            print(f"Match not found in betminer: {home_team} vs {away_team}")
            return {}

        # 提取betminer数据
        home_team_id = target_match['home_team']['id']
        away_team_id = target_match['away_team']['id']
        league_id = target_match['competition']['id']

        # 2. 并行获取API-Football数据
        standings, injuries, h2h, home_stats, away_stats = await asyncio.gather(
            self.fetch_standings(league_id),
            self.fetch_injuries(home_team_id, league_id),
            self.fetch_head_to_head(home_team_id, away_team_id),
            self.fetch_team_stats(home_team_id, league_id),
            self.fetch_team_stats(away_team_id, league_id),
            return_exceptions=True
        )

        # 3. 整合所有数据
        return {
            'match_info': {
                'home_team': target_match['home_team']['name'],
                'away_team': target_match['away_team']['name'],
                'home_team_id': home_team_id,
                'away_team_id': away_team_id,
                'league': target_match['competition']['name'],
                'league_id': league_id,
                'match_date': match_date,
                'status': target_match['status'],
            },
            'odds_data': {
                'home_odds': float(target_match['odds']['home_win']),
                'draw_odds': float(target_match['odds']['draw']),
                'away_odds': float(target_match['odds']['away_win']),
                'probabilities': target_match['probabilities'],
                'edge_analysis': target_match['edge_analysis'],
            },
            'form_data': {
                'home_form': list(target_match['form']['home']),
                'away_form': list(target_match['form']['away']),
                'home_btts': list(target_match.get('form', {}).get('home_btts', '')),
                'away_btts': list(target_match.get('form', {}).get('away_btts', '')),
            },
            'standings': self._extract_standings(standings, home_team_id, away_team_id)
                if not isinstance(standings, Exception) else {},
            'injuries': self._extract_injuries(injuries) if not isinstance(injuries, Exception) else [],
            'h2h': self._extract_h2h(h2h) if not isinstance(h2h, Exception) else [],
            'home_stats': home_stats if not isinstance(home_stats, Exception) else {},
            'away_stats': away_stats if not isinstance(away_stats, Exception) else {},
            'predictions': target_match.get('predictions', {}),
            'value_analysis': {
                'best_value': target_match.get('best_value'),
                'worst_value': target_match.get('worst_value'),
                'is_trap': target_match.get('is_trap', False),
                'value_score': target_match.get('value_score', 0),
            }
        }

    def _extract_standings(self, standings: List[Dict], home_id: int, away_id: int) -> Dict:
        """从standings数据中提取主客队排名"""
        result = {'home_position': None, 'away_position': None}

        if standings and len(standings) > 0:
            table = standings[0].get('league', {}).get('standings', [[]])[0]

            for team in table:
                team_id = team.get('team', {}).get('id')
                if team_id == home_id:
                    result['home_position'] = team.get('rank')
                elif team_id == away_id:
                    result['away_position'] = team.get('rank')

        return result

    def _extract_injuries(self, injuries: List[Dict]) -> List[Dict]:
        """从sidelines数据中提取伤停"""
        result = []

        for sideline in injuries:
            player = sideline.get('player', {})
            if player:
                result.append({
                    'name': player.get('name'),
                    'position': player.get('position'),
                    'reason': sideline.get('reason', ''),
                    'type': sidelined.get('type', 'injury'),
                })

        return result

    def _extract_h2h(self, h2h: List[Dict]) -> List[Dict]:
        """提取历史交锋数据"""
        result = []

        for match in h2h:
            teams = match.get('teams', {})
            score = match.get('score', {})
            result.append({
                'date': match.get('fixture', {}).get('date'),
                'home_team': teams.get('home', {}).get('name'),
                'away_team': teams.get('away', {}).get('name'),
                'home_score': score.get('fulltime', {}).get('home'),
                'away_score': score.get('fulltime', {}).get('away'),
                'winner': match.get('teams', {}).get('winner'),  # 'home', 'away', or 'draw'
            })

        return result

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            'cache_size': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'cached_keys': list(self.cache.keys())
        }

    def clear_cache(self, category: Optional[str] = None):
        """清除缓存"""
        if category:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(category)]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()


# 测试
async def test_hybrid_fetcher():
    """测试混合API获取器"""
    print("=" * 60)
    print("混合API获取器测试")
    print("=" * 60)

    fetcher = HybridAPIFetcher()

    # 测试1: 获取今天的数据
    print("\n测试1: 获取今天的betminer数据...")
    today = datetime.now().strftime('%Y-%m-%d')
    betminer_data = await fetcher.fetch_betminer_edge_analysis(today)
    print(f"[OK] 获取到 {len(betminer_data)} 场比赛")

    if betminer_data:
        match = betminer_data[0]
        print(f"\n示例比赛:")
        print(f"  {match['home_team']['name']} vs {match['away_team']['name']}")
        print(f"  联赛: {match['competition']['name']}")
        print(f"  比分: {match['score']['home']}-{match['score']['away']}")
        print(f"  近期状态: 主队 {match['form']['home']}, 客队 {match['form']['away']}")
        print(f"  价值分析: best_value={match.get('best_value')}, is_trap={match.get('is_trap')}")

    # 测试2: 获取完整比赛数据
    if betminer_data and len(betminer_data) > 0:
        match = betminer_data[0]
        print("\n\n测试2: 获取完整比赛数据...")
        print(f"比赛: {match['home_team']['name']} vs {match['away_team']['name']}")

        complete_data = await fetcher.fetch_complete_match_data(
            home_team=match['home_team']['name'],
            away_team=match['away_team']['name'],
            league=match['competition']['name'],
            match_date=today
        )

        print(f"[OK] 完整数据获取成功!")
        print(f"  - match_info: {complete_data.get('match_info', {})}")
        print(f"  - odds_data: {list(complete_data.get('odds_data', {}).keys())}")
        print(f"  - form_data: {complete_data.get('form_data', {})}")
        print(f"  - standings: {complete_data.get('standings', {})}")
        print(f"  - injuries: {len(complete_data.get('injuries', []))} 条")
        print(f"  - h2h: {len(complete_data.get('h2h', []))} 场")

    print("\n缓存统计:")
    print(fetcher.get_cache_stats())


if __name__ == '__main__':
    asyncio.run(test_hybrid_fetcher())
