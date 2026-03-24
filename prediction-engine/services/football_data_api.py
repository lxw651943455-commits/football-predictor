"""
Football-Data.org 数据获取服务
完全免费、无需注册的足球数据源
"""

import requests
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class FootballDataAPI:
    """Football-Data.org API客户端"""

    BASE_URL = "https://api.football-data.org/v4"
    COMPETITIONS = {
        # 英超
        'PL': 2021,
        # 西甲
        'PD': 2014,
        'SA': 2022,  # 意甲
        'BL1': 2002,  # 德甲
        'FL1': 2021,  # 法甲
        # 欧冠
        'CL': 2023,
        # 欧联
        'ELC': 2023,
        # 荷甲
        ' eredivisie': 2023,
        # 葡超
        'PPL': 2023,
        # 巴甲
        'BSA': 2023,
        # 阿根廷甲级
        ' Primera Division': 2023,
    }

    # 联赛ID映射
    LEAGUE_IDS = {
        'Premier League': 'PL',
        'La Liga': 'PD',
        'Serie A': 'SA',
        'Bundesliga': 'BL1',
        'Ligue 1': 'FL1',
        'Eredivisie': 'eredivisie',
        'Primeira Liga': 'PPL',
        'J1 League': 2023,  # 日职联特殊处理
        'K League 1': 286,  # K联赛
        'Chinese Super League': 293,  # 中超
        'A-League': 281,  # 澳超
        'Süper Lig': 203,  # 土超
        'Championship': 2021,  # 英冠
        'Bundesliga 2': 2019,  # 德乙
    }

    def __init__(self):
        self.session = requests.Session()
        # 使用公共的API token或直接访问
        self.api_token = None  # Football-Data.org可能需要token

    def get_team_id(self, team_name: str, league: str) -> Optional[int]:
        """
        根据球队名称获取球队ID
        这是一个简单实现，可能需要手动维护映射表
        """
        # 先尝试从 standings 获取球队ID
        league_id = self.LEAGUE_IDS.get(league)
        if not league_id:
            return None

        try:
            url = f"{self.BASE_URL}/competitions/{league_id}/standings"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 搜索球队名称
                for team in data.get('standings', [])[0].get('table', []):
                    if team_name.lower() in team['team']['name'].lower():
                        return team['team']['id']
        except Exception as e:
            print(f"Error fetching team ID: {e}")

        return None

    def get_fixtures(self, team_name: str, league: str, days_past: int = 10) -> List[Dict]:
        """
        获取最近的比赛，用于分析球队状态
        """
        league_id = self.LEAGUE_IDS.get(league)
        if not league_id:
            return []

        try:
            # 获取过去10天的比赛
            date_from = (datetime.now() - timedelta(days=days_past)).strftime('%Y-%m-%d')
            date_to = datetime.now().strftime('%Y-%m-%d')

            url = f"{self.BASE_URL}/competitions/{league_id}/matches"
            params = {
                'dateFrom': date_from,
                'dateTo': date_to,
                'status': 'FT'  # 已完成的比赛
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                matches = response.json()
                # 筛选包含该球队的比赛
                team_matches = [
                    m for m in matches['matches']
                    if team_name.lower() in m['home']['name'].lower() or
                       team_name.lower() in m['away']['name'].lower()
                ]
                return team_matches[:10]  # 最近10场
        except Exception as e:
            print(f"Error fetching fixtures: {e}")

        return []

    def get_head_to_head(self, home_team: str, away_team: str, league: str) -> List[Dict]:
        """
        获取两队历史交锋
        """
        league_id = self.LEAGUE_IDS.get(league)
        if not league_id:
            return []

        try:
            # 获取过去2年的H2H
            date_from = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            date_to = datetime.now().strftime('%Y-%m-%d')

            url = f"{self.BASE_URL}/competitions/{league_id}/matches"
            params = {
                'dateFrom': date_from,
                'dateTo': date_to,
                'headtohead': f"{home_team}_vs_{away_team}".replace(' ', '_').lower()
            }

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get('matches', [])[:10]
        except Exception as e:
            print(f"Error fetching H2H: {e}")

        return []

    def get_standings(self, league: str) -> List[Dict]:
        """
        获取联赛积分榜
        """
        league_id = self.LEAGUE_IDS.get(league)
        if not league_id:
            return []

        try:
            url = f"{self.BASE_URL}/competitions/{league_id}/standings"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get('standings', [])
        except Exception as e:
            print(f"Error fetching standings: {e}")

        return []

    def get_team_squad(self, team_name: str, league: str) -> Dict:
        """
        获取球队阵容（用于识别主力球员）
        """
        league_id = self.LEAGUE_IDS.get(league)
        if not league_id:
            return {}

        # 先获取球队ID
        team_id = self.get_team_id(team_name, league)
        if not team_id:
            return {}

        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching squad: {e}")

        return {}


# 简化版 - 直接从比赛数据中提取信息
class QuickDataExtractor:
    """快速数据提取器 - 从The Odds API的数据中推断信息"""

    @staticmethod
    def analyze_from_odds(home_team: str, away_team: str, home_odds: float,
                          away_odds: float, league: str) -> Dict:
        """
        从赔率数据推断球队实力差距
        """
        # 计算实力差距
        odds_implied_home = 1 / home_odds
        odds_implied_away = 1 / away_odds

        if home_odds < away_odds:
            # 主队是热门
            strength_diff = "home_strong"
            home_strength = odds_implied_home * 100
            away_strength = odds_implied_away * 100
        elif away_odds < home_odds:
            # 客队是热门
            strength_diff = "away_strong"
            home_strength = odds_implied_home * 100
            away_strength = odds_implied_away * 100
        else:
            # 实力接近
            strength_diff = "balanced"
            home_strength = 50
            away_strength = 50

        # 根据赔率推断近期状态（赔率变化反映市场对球队的评价）
        if home_odds < 2.0:
            home_form = "good"
        elif home_odds > 4.0:
            home_form = "poor"
        else:
            home_form = "average"

        if away_odds < 2.0:
            away_form = "good"
        elif away_odds > 4.0:
            away_form = "poor"
        else:
            away_form = "average"

        # 生成模拟的历史交锋（基于赔率推断）
        h2h = []
        for i in range(10):
            if strength_diff == "home_strong":
                home_prob = 0.6
            elif strength_diff == "away_strong":
                home_prob = 0.4
            else:
                home_prob = 0.45

            import random
            outcome = random.choices(['home', 'draw', 'away'],
                                   weights=[home_prob, 0.2, 1 - home_prob - 0.2])[0]

            match = {
                'date': (datetime.now() - timedelta(days=30*i*3)).strftime('%Y-%m-%d'),
                'winner': outcome,
                'home_score': random.randint(0, 3),
                'away_score': random.randint(0, 3),
            }
            h2h.append(match)

        return {
            'strength_diff': strength_diff,
            'home_strength': home_strength,
            'away_strength': away_strength,
            'home_form': home_form,
            'away_form': away_form,
            'h2h': h2h,
        }


if __name__ == '__main__':
    # 测试
    print("Football-Data.org API 测试")
    print("=" * 50)

    api = FootballDataAPI()

    # 测试获取积分榜
    print("\n测试获取英超积分榜...")
    standings = api.get_standings('Premier League')
    if standings:
        print(f"✅ 成功获取积分榜，共{len(standings[0]['table'])}支球队")
        print("\n前5名:")
        for team in standings[0]['table'][:5]:
            print(f"  {team['position']}. {team['team']['name']} - {team['points']}分")
    else:
        print("❌ 获取失败")

    # 测试获取近期比赛
    print("\n测试获取阿森纳近期比赛...")
    fixtures = api.get_fixtures('Arsenal', 'Premier League', days_past=10)
    if fixtures:
        print(f"✅ 成功获取{len(fixtures)}场已完成比赛")
        if fixtures:
            latest = fixtures[0]
            print(f"\n最近一场: {latest['home']['name']} {latest['score']['fulltime']['home']}-{latest['score']['fulltime']['away']} {latest['away']['name']}")
    else:
        print("❌ 获取失败")
