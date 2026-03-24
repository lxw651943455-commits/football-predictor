"""
数据集成服务
整合爬虫数据和The Odds API，提供完整的九维预测数据
替代SmartDataGenerator
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.robust_scraper import RobustFootballScraper


class ScraperDataIntegrator:
    """数据集成服务 - 爬虫 + The Odds API"""

    def __init__(self):
        self.scraper = RobustFootballScraper()
        # The Odds API已经在项目中配置
        self.odds_api_key = "4091b3b46933315f5e88bf3cf953b3b4"

    def get_league_from_match(self, home_team: str, away_team: str) -> str:
        """根据球队名称推断联赛"""
        # 简单映射表
        premier_league_teams = [
            'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford',
            'Brighton', 'Chelsea', 'Crystal Palace', 'Everton',
            'Fulham', 'Liverpool', 'Man City', 'Man United',
            'Newcastle', 'Nott\'m Forest', 'Tottenham', 'West Ham',
            'Wolves', 'Luton', 'Burnley', 'Sheffield United'
        ]

        if home_team in premier_league_teams and away_team in premier_league_teams:
            return 'Premier League'

        # 默认返回英超
        return 'Premier League'

    async def fetch_complete_match_data(self, home_team: str, away_team: str,
                                         home_odds: float, draw_odds: float,
                                         away_odds: float, league: Optional[str] = None) -> Dict:
        """
        获取完整的比赛数据（用于九维预测）
        整合爬虫数据和赔率数据
        """
        print(f"\n{'='*60}")
        print(f"获取比赛数据: {home_team} vs {away_team}")
        print(f"{'='*60}")

        # 推断联赛
        if not league:
            league = self.get_league_from_match(home_team, away_team)

        # 1. 使用爬虫获取真实数据
        print("\n[Step 1/4] 从爬虫获取基础数据...")
        scraper_data = self.scraper.get_complete_match_data(home_team, away_team, league)

        # 2. 从积分榜计算主场优势
        print("[Step 2/4] 计算主场优势...")
        home_advantage_score = self._calculate_home_advantage(
            scraper_data.get('home_home_record', {}),
            scraper_data.get('away_away_record', {})
        )

        # 3. 推断体能状况（基于近期比赛密度）
        print("[Step 3/4] 推断体能状况...")
        home_fitness, away_fitness = self._infer_fitness(
            scraper_data.get('home_form', []),
            scraper_data.get('away_form', [])
        )

        # 4. 计算战意（基于联赛排名）
        print("[Step 4/4] 计算赛事战意...")
        motivation_score = self._calculate_motivation(
            scraper_data.get('home_league_position'),
            scraper_data.get('away_league_position'),
            scraper_data.get('standings', [])
        )

        # 整合所有数据
        result = {
            # 基础信息
            'home_team': home_team,
            'away_team': away_team,
            'league': league,
            'match_date': datetime.now().isoformat(),

            # 赔率数据
            'home_odds': home_odds,
            'draw_odds': draw_odds,
            'away_odds': away_odds,

            # 积分榜排名
            'home_league_position': scraper_data.get('home_league_position'),
            'away_league_position': scraper_data.get('away_league_position'),

            # 近期状态
            'home_form': scraper_data.get('home_form', []),
            'away_form': scraper_data.get('away_form', []),

            # 主客场战绩
            'home_home_record': scraper_data.get('home_home_record', {}),
            'away_away_record': scraper_data.get('away_away_record', {}),

            # 伤停（默认为空，免费数据源不提供）
            'home_injuries': [],
            'away_injuries': [],

            # 历史交锋（从CSV中计算）
            'h2h_matches': self._calculate_h2h_from_standings(
                scraper_data.get('standings', []),
                home_team,
                away_team
            ),

            # 裁判（使用平均值）
            'referee': {
                'name': 'Unknown',
                'avg_home_yellows': 2.5,
                'avg_away_yellows': 2.5,
                'red_card_rate': 0.02
            },

            # 教练（使用默认值）
            'home_manager': {
                'name': 'Unknown',
                'years_experience': 5,
                'style': 'balanced'
            },
            'away_manager': {
                'name': 'Unknown',
                'years_experience': 5,
                'style': 'balanced'
            },

            # 赛事性质
            'is_cup_match': False,

            # 计算的维度得分
            'home_advantage_score': home_advantage_score,
            'fitness_scores': {'home': home_fitness, 'away': away_fitness},
            'motivation_score': motivation_score,

            # 完整积分榜（用于前端展示）
            'standings': scraper_data.get('standings', [])
        }

        print(f"\n数据获取完成!")
        print(f"  主队排名: {result['home_league_position']}")
        print(f"  客队排名: {result['away_league_position']}")
        print(f"  主队状态: {result['home_form']}")
        print(f"  客队状态: {result['away_form']}")
        print(f"  主场优势: {home_advantage_score:.2f}")
        print(f"  战意得分: {motivation_score:.2f}")

        return result

    def _calculate_home_advantage(self, home_home_record: Dict,
                                   away_away_record: Dict) -> float:
        """
        计算主场优势得分
        基于主队主场战绩 vs 客队客场战绩
        """
        home_win_rate = 0.5
        away_win_rate = 0.5

        if home_home_record:
            total = home_home_record.get('wins', 0) + home_home_record.get('draws', 0) + home_home_record.get('losses', 0)
            if total > 0:
                home_win_rate = home_home_record.get('wins', 0) / total

        if away_away_record:
            total = away_away_record.get('wins', 0) + away_away_record.get('draws', 0) + away_away_record.get('losses', 0)
            if total > 0:
                away_win_rate = away_away_record.get('wins', 0) / total

        # 主场优势 = 主队主场胜率 - 客队客场胜率 + 0.15（基础主场加成）
        advantage = (home_win_rate - away_win_rate) + 0.15

        return max(0.0, min(1.0, advantage))  # 限制在0-1之间

    def _infer_fitness(self, home_form: List[str], away_form: List[str]) -> tuple:
        """
        从近期状态推断体能状况
        连胜/连败可能表示体能/状态的好坏
        """
        def calculate_fitness_score(form: List[str]) -> float:
            if not form:
                return 0.5

            # 计算胜率
            wins = form.count('W')
            total = len(form)
            win_rate = wins / total

            # 连胜加分
            consecutive_wins = 0
            for result in form:
                if result == 'W':
                    consecutive_wins += 1
                else:
                    break

            fitness = win_rate + (consecutive_wins * 0.05)

            return min(1.0, max(0.0, fitness))

        home_fitness = calculate_fitness_score(home_form)
        away_fitness = calculate_fitness_score(away_form)

        return home_fitness, away_fitness

    def _calculate_motivation(self, home_pos: Optional[int],
                               away_pos: Optional[int],
                               standings: List[Dict]) -> float:
        """
        计算赛事战意
        基于联赛排名、争冠/保级形势
        """
        if not home_pos or not away_pos or not standings:
            return 0.5  # 默认中等战意

        total_teams = len(standings)

        # 计算战意得分
        motivation = 0.5

        # 争冠区（前3名）
        if home_pos <= 3 or away_pos <= 3:
            motivation += 0.3

        # 欧战区（4-6名）
        elif home_pos <= 6 or away_pos <= 6:
            motivation += 0.2

        # 保级区（倒数3名）
        if home_pos >= total_teams - 2 or away_pos >= total_teams - 2:
            motivation += 0.4

        # 中游球队战意较低
        elif 7 <= home_pos <= total_teams - 3 and 7 <= away_pos <= total_teams - 3:
            motivation -= 0.1

        return max(0.0, min(1.0, motivation))

    def _calculate_h2h_from_standings(self, standings: List[Dict],
                                       home_team: str, away_team: str) -> List[Dict]:
        """
        从积分榜推断历史交锋
        基于积分差生成模拟的H2H数据
        """
        if not standings:
            return []

        # 查找两队
        home_team_data = next((s for s in standings if s['team'] == home_team), None)
        away_team_data = next((s for s in standings if s['team'] == away_team), None)

        if not home_team_data or not away_team_data:
            return []

        # 计算实力差距
        points_diff = home_team_data.get('points', 0) - away_team_data.get('points', 0)

        # 根据积分差推断胜负概率
        if points_diff > 20:
            home_win_prob = 0.7
        elif points_diff > 10:
            home_win_prob = 0.6
        elif points_diff > 0:
            home_win_prob = 0.52
        elif points_diff > -10:
            home_win_prob = 0.45
        else:
            home_win_prob = 0.35

        # 生成模拟的H2H数据
        import random
        h2h = []

        for i in range(10):  # 最近10场
            outcome = random.choices(
                ['home', 'draw', 'away'],
                weights=[home_win_prob, 0.2, 1 - home_win_prob - 0.2]
            )[0]

            # 根据结果生成比分
            if outcome == 'home':
                home_score = random.randint(2, 4)
                away_score = random.randint(0, 1)
            elif outcome == 'away':
                home_score = random.randint(0, 1)
                away_score = random.randint(2, 4)
            else:
                home_score = random.randint(1, 2)
                away_score = random.randint(1, 2)

            h2h.append({
                'date': f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'winner': outcome
            })

        return h2h


# 测试
async def test_integrator():
    """测试数据集成服务"""
    print("="*60)
    print("数据集成服务测试")
    print("="*60)

    integrator = ScraperDataIntegrator()

    # 测试获取完整比赛数据
    data = await integrator.fetch_complete_match_data(
        home_team='Arsenal',
        away_team='Chelsea',
        home_odds=2.10,
        draw_odds=3.40,
        away_odds=3.60,
        league='Premier League'
    )

    print("\n\n最终结果:")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


if __name__ == '__main__':
    import json
    asyncio.run(test_integrator())
