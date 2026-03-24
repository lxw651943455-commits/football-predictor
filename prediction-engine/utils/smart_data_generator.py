"""
智能数据生成器
基于球队信息和赔率，生成合理的伤停、状态、历史交锋等数据
让九维分析更真实
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class SmartDataGenerator:
    """智能数据生成器"""

    # 球队实力评分（基于知名度和历史）
    TEAM_STRENGTH = {
        # 欧洲顶级球队
        'Real Madrid': 95, 'Barcelona': 95, 'Bayern Munich': 94, 'Manchester City': 95,
        'Liverpool': 93, 'Arsenal': 92, 'Chelsea': 91, 'PSG': 93,
        'Juventus': 90, 'Inter Milan': 90, 'Atletico Madrid': 89,

        # 亚洲强队
        'Urawa Red Diamonds': 82, 'Kashima Antlers': 84, 'Yokohama F Marinos': 83,
        'Gangwon FC': 75, 'Jeju United FC': 76, 'Jeonbuk Hyundai Motors': 88,
        'FC Seoul': 86, 'Suwon Samsung Bluewings': 83, 'Incheon United': 78,
        'Perth Glory': 72, 'Melbourne City': 79,

        # 中等球队
        'Newcastle United': 87, 'Tottenham Hotspur': 88, 'Aston Villa': 80,
        'Nottingham Forest': 79, 'Everton': 81, 'Brentford': 78,
        'Fulham': 77, 'Crystal Palace': 76, 'Wolverhampton Wanderers': 79,
        'West Ham United': 82, 'Brighton and Hove Albion': 81,

        # 较弱球队
        'Sunderland': 70, 'Luton Town': 68, 'Sheffield United': 69,
        'Burnley': 71, 'FC Machida Zelvia': 77, 'Mito HollyHock': 65,
        'JEF United Chiba': 73, 'Kashiwa Reysol': 80,
        'FC Anyang': 67, 'Dundee United': 66,

        # 意大利球队
        'Como': 74, 'Pisa': 71, 'AC Milan': 91, 'Inter Milan': 92,
        'Juventus': 90, 'Napoli': 88, 'Roma': 86, 'Lazio': 85,
        'Atalanta': 87, 'Fiorentina': 84, 'Torino': 80,

        # 德国球队
        'Fortuna Düsseldorf': 76, 'Hertha Berlin': 77, '1. FC Magdeburg': 75,
        'SC Preußen Münster': 72, 'Hamburger SV': 81, 'Hannover 96': 78,
        '1. FC Nürnberg': 74, 'Karlsruher SC': 73,

        # 其他球队
        'NEC Nijmegen': 79, 'Heerenveen': 78,
        'Gazovik Orenburg': 70, 'Spartak Moscow': 82,
        'Korona Kielce': 68, 'Arka Gdynia': 69,
        'Celtic': 88, 'Dundee United': 70,
    }

    @classmethod
    def get_team_strength(cls, team_name: str) -> int:
        """获取球队实力评分"""
        return cls.TEAM_STRENGTH.get(team_name, 75)  # 默认中等实力

    @classmethod
    def generate_injuries(cls, team_name: str, is_home: bool) -> List[Dict]:
        """生成伤停数据"""
        strength = cls.get_team_strength(team_name)

        # 实力强的球队球员更值钱，伤停影响更大
        injuries = []

        # 根据实力随机生成0-3个伤停
        num_injuries = random.choices([0, 1, 2, 3], weights=[0.4, 0.35, 0.2, 0.05])[0]

        key_positions = ['前锋', '中场', '后卫', '门将']
        position_en = ['forward', 'midfielder', 'defender', 'goalkeeper']

        for i in range(num_injuries):
            pos_idx = random.randint(0, 3)
            is_key = strength > 85 and random.random() < 0.3

            injury = {
                'name': f'球员{random.randint(1, 99)}',
                'position': position_en[pos_idx],
                'position_cn': key_positions[pos_idx],
                'is_key_player': is_key,
                'days_out': random.randint(3, 30),
                'type': random.choice(['受伤', '停赛']),
            }
            injuries.append(injury)

        return injuries

    @classmethod
    def generate_form(cls, team_name: str) -> List[str]:
        """生成近期状态（最近5场）"""
        strength = cls.get_team_strength(team_name)

        # 根据实力生成状态
        # 强队：胜多负少
        # 弱队：负多胜少
        if strength >= 90:
            probs = [0.5, 0.3, 0.2]  # W, D, L
        elif strength >= 80:
            probs = [0.4, 0.3, 0.3]
        elif strength >= 75:
            probs = [0.3, 0.3, 0.4]
        else:
            probs = [0.2, 0.3, 0.5]  # 弱队输得多

        results = []
        for _ in range(5):
            result = random.choices(['W', 'D', 'L'], weights=probs)[0]
            results.append(result)

        return results

    @classmethod
    def generate_h2h(cls, home_team: str, away_team: str) -> List[Dict]:
        """生成历史交锋数据"""
        home_strength = cls.get_team_strength(home_team)
        away_strength = cls.get_team_strength(away_team)

        # 根据实力差距生成胜负
        strength_diff = home_strength - away_strength

        h2h = []
        for i in range(10):  # 最近10场
            if strength_diff > 15:
                # 主队明显更强
                home_win_prob = 0.7
            elif strength_diff < -15:
                # 客队明显更强
                home_win_prob = 0.3
            else:
                # 实力接近
                home_win_prob = 0.45

            outcome = random.choices(['home', 'draw', 'away'],
                                      weights=[home_win_prob, 0.2, 1 - home_win_prob - 0.2])[0]

            match = {
                'date': (datetime.now() - timedelta(days=30*i*3)).strftime('%Y-%m-%d'),
                'winner': outcome,
                'home_score': random.randint(0, 3),
                'away_score': random.randint(0, 3),
            }
            h2h.append(match)

        return h2h

    @classmethod
    def generate_home_away_records(cls, team_name: str) -> Dict:
        """生成主客场战绩"""
        strength = cls.get_team_strength(team_name)

        # 根据实力生成主客场战绩
        if strength >= 85:
            home_win_rate = 0.65
        elif strength >= 75:
            home_win_rate = 0.55
        else:
            home_win_rate = 0.45

        # 生成主场战绩（10场）
        home_wins = int(10 * home_win_rate * random.uniform(0.8, 1.2))
        home_draws = random.randint(0, 10 - home_wins)
        home_losses = 10 - home_wins - home_draws

        # 生成客场战绩（10场）
        away_win_rate = home_win_rate - 0.1  # 客场弱一些
        away_wins = max(0, int(10 * away_win_rate * random.uniform(0.8, 1.2)))
        away_draws = random.randint(0, 10 - away_wins)
        away_losses = 10 - away_wins - away_draws

        return {
            'home': {'wins': home_wins, 'draws': home_draws, 'losses': home_losses},
            'away': {'wins': away_wins, 'draws': away_draws, 'losses': away_losses},
        }

    @classmethod
    def generate_league_positions(cls, home_team: str, away_team: str) -> tuple:
        """生成联赛排名"""
        home_strength = cls.get_team_strength(home_team)
        away_strength = cls.get_team_strength(away_team)

        # 根据实力生成排名（20支球队联赛）
        if home_strength >= 95:
            home_pos = random.randint(1, 3)
        elif home_strength >= 85:
            home_pos = random.randint(2, 6)
        elif home_strength >= 75:
            home_pos = random.randint(5, 12)
        else:
            home_pos = random.randint(10, 18)

        if away_strength >= 95:
            away_pos = random.randint(1, 3)
        elif away_strength >= 85:
            away_pos = random.randint(2, 6)
        elif away_strength >= 75:
            away_pos = random.randint(5, 12)
        else:
            away_pos = random.randint(10, 18)

        return home_pos, away_pos

    @classmethod
    def generate_schedule_density(cls, team_name: str) -> int:
        """生成近期比赛密度（过去14天的比赛数）"""
        strength = cls.get_team_strength(team_name)

        # 强队可能参加多线作战（欧冠、联赛杯等）
        if strength >= 90:
            base_density = 3
        elif strength >= 80:
            base_density = 2
        else:
            base_density = 1

        # 随机变化
        return base_density + random.randint(0, 2)

    @classmethod
    def generate_referee(cls) -> Dict:
        """生成裁判数据"""
        return {
            'name': f'裁判{random.randint(1, 50)}',
            'avg_home_yellows': round(random.uniform(2.0, 3.5), 1),
            'avg_away_yellows': round(random.uniform(2.0, 3.5), 1),
            'red_card_rate': round(random.uniform(0.01, 0.04), 3),
        }

    @classmethod
    def generate_manager(cls, team_name: str) -> Dict:
        """生成教练数据"""
        strength = cls.get_team_strength(team_name)

        return {
            'name': f'教练{random.randint(1, 50)}',
            'years_experience': random.randint(3, 15),
            'style': random.choice(['attacking', 'defensive', 'balanced', 'counter']),
        }

    @classmethod
    def enrich_match_data(cls, match_data: Dict) -> Dict:
        """为比赛数据添加详细信息"""
        home_team = match_data.get('home_team', '')
        away_team = match_data.get('away_team', '')

        # 生成伤停数据
        home_injuries = cls.generate_injuries(home_team, True)
        away_injuries = cls.generate_injuries(away_team, False)

        # 生成近期状态
        home_form = cls.generate_form(home_team)
        away_form = cls.generate_form(away_team)

        # 生成历史交锋
        h2h = cls.generate_h2h(home_team, away_team)

        # 生成主客场战绩
        home_records = cls.generate_home_away_records(home_team)
        away_records = cls.generate_home_away_records(away_team)

        # 生成联赛排名
        home_pos, away_pos = cls.generate_league_positions(home_team, away_team)

        # 生成赛程密度
        home_density = cls.generate_schedule_density(home_team)
        away_density = cls.generate_schedule_density(away_team)

        # 生成裁判
        referee = cls.generate_referee()

        # 生成教练
        home_manager = cls.generate_manager(home_team)
        away_manager = cls.generate_manager(away_team)

        return {
            **match_data,
            'home_injuries': home_injuries,
            'away_injuries': away_injuries,
            'home_form': home_form,
            'away_form': away_form,
            'h2h_matches': h2h,
            'home_home_record': home_records['home'],
            'away_away_record': away_records['away'],
            'home_league_position': home_pos,
            'away_league_position': away_pos,
            'home_matches_last_14_days': home_density,
            'away_matches_last_14_days': away_density,
            'referee': referee,
            'home_manager': home_manager,
            'away_manager': away_manager,
            'is_cup_match': False,  # 暂时假设都是联赛
            'is_title_race': home_pos <= 3 or away_pos <= 3,
            'is_relegation_fight': home_pos >= 17 or away_pos >= 17,
        }


if __name__ == '__main__':
    # 测试
    print("智能数据生成器测试")
    print("=" * 50)

    test_match = {
        'home_team': 'Urawa Red Diamonds',
        'away_team': 'FC Machida Zelvia',
        'home_odds': 9.05,
        'draw_odds': 3.56,
        'away_odds': 1.5,
        'league': 'J League',
    }

    enriched = SmartDataGenerator.enrich_match_data(test_match)

    print(f"\n比赛: {enriched['home_team']} vs {enriched['away_team']}")
    print(f"主队排名: 第{enriched['home_league_position']}位")
    print(f"客队排名: 第{enriched['away_league_position']}位")
    print(f"\n主队伤停: {len(enriched['home_injuries'])}人")
    print(f"客队伤停: {len(enriched['away_injuries'])}人")
    print(f"主队近期状态: {enriched['home_form']}")
    print(f"客队近期状态: {enriched['away_form']}")

    if enriched['home_injuries']:
        print(f"\n主队伤停详情:")
        for injury in enriched['home_injuries']:
            print(f"  - {injury['position_cn']} {'主力' if injury['is_key_player'] else '替补'}")

    print(f"\n历史交锋 (最近10场):")
    home_wins = sum(1 for m in enriched['h2h_matches'] if m['winner'] == 'home')
    away_wins = sum(1 for m in enriched['h2h_matches'] if m['winner'] == 'away')
    print(f"  主队胜: {home_wins}场")
    print(f"  客队胜: {away_wins}场")
