"""
增强版足球数据爬虫
使用多个数据源，提高成功率
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from typing import Dict, List, Optional
from datetime import datetime


class RobustFootballScraper:
    """增强版足球数据爬虫 - 多数据源"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 多个数据源（按优先级排序）
        self.sources = {
            'fbref': 'https://fbref.com',
            'brazil_scraper': 'https://brazil-api.herokuapp.com/api',
            'football-data': 'https://www.football-data.org',
        }

        # 球队名称映射表（常见别名 -> CSV中的标准名称）
        self.team_name_mapping = {
            # 英超
            'Man United': 'Man United',
            'Manchester United': 'Man United',
            'Man City': 'Man City',
            'Manchester City': 'Man City',
            'Spurs': 'Tottenham',
            'Tottenham Hotspur': 'Tottenham',
            'Wolves': 'Wolves',
            'Wolverhampton': 'Wolves',
            'Newcastle': 'Newcastle',
            'Newcastle United': 'Newcastle',
            'Nottingham Forest': 'Nott\'m Forest',
            'Nottm Forest': 'Nott\'m Forest',
            'Sheffield United': 'Sheffield United',
            'Burnley': 'Burnley',
            'Luton': 'Luton',
            'West Ham': 'West Ham',
            'Crystal Palace': 'Crystal Palace',
            'Aston Villa': 'Aston Villa',
            'Bournemouth': 'Bournemouth',
            'Brentford': 'Brentford',
            'Brighton': 'Brighton',
            'Chelsea': 'Chelsea',
            'Everton': 'Everton',
            'Fulham': 'Fulham',
            'Liverpool': 'Liverpool',
            'Arsenal': 'Arsenal',

            # 西甲
            'Real Madrid': 'Real Madrid',
            'Barcelona': 'Barcelona',
            'Atlético Madrid': 'Atletico Madrid',
            'Atletico Madrid': 'Atletico Madrid',
            'Sevilla': 'Sevilla',
            'Real Sociedad': 'Real Sociedad',
            'Real Betis': 'Real Betis',
            'Villarreal': 'Villarreal',
            'Athletic Bilbao': 'Athletic Club',
            'Valencia': 'Valencia',
            'Celta Vigo': 'Celta Vigo',

            # 意甲
            'Inter': 'Inter',
            'Inter Milan': 'Inter',
            'AC Milan': 'Milan',
            'Milan': 'Milan',
            'Juventus': 'Juventus',
            'Juve': 'Juventus',
            'Napoli': 'Napoli',
            'Roma': 'Roma',
            'AS Roma': 'Roma',
            'Lazio': 'Lazio',
            'Atalanta': 'Atalanta',
            'Fiorentina': 'Fiorentina',

            # 德甲
            'Bayern Munich': 'Bayern Munich',
            'Bayern': 'Bayern Munich',
            'Dortmund': 'Dortmund',
            'Borussia Dortmund': 'Dortmund',
            'Leverkusen': 'Leverkusen',
            'Bayer Leverkusen': 'Leverkusen',
            'RB Leipzig': 'RB Leipzig',
            'Leipzig': 'RB Leipzig',
            'Frankfurt': 'Ein Frankfurt',
            'Eintracht Frankfurt': 'Ein Frankfurt',
            'Wolfsburg': 'Wolfsburg',
            'Freiburg': 'Freiburg',
            'Mönchengladbach': 'M\'gladbach',
            'Monchengladbach': 'M\'gladbach',
            'Borussia Mönchengladbach': 'M\'gladbach',
            'Mainz': 'Mainz',
            'Union Berlin': 'Union Berlin',

            # 法甲
            'PSG': 'Paris SG',
            'Paris Saint-Germain': 'Paris SG',
            'Paris SG': 'Paris SG',
            'Monaco': 'Monaco',
            'Marseille': 'Marseille',
            'Lyon': 'Lyon',
            'Lille': 'Lille',
            'Nice': 'Nice',
            'Lens': 'Lens',
        }

    def normalize_team_name(self, team_name: str) -> str:
        """标准化球队名称"""
        if not team_name:
            return team_name

        # 直接查找映射
        if team_name in self.team_name_mapping:
            return self.team_name_mapping[team_name]

        # 尝试模糊匹配
        for alias, standard_name in self.team_name_mapping.items():
            if alias.lower() in team_name.lower() or team_name.lower() in alias.lower():
                return standard_name

        # 没找到映射，返回原名
        return team_name

    def get_standings_from_fbref(self, league: str) -> List[Dict]:
        """
        从FBref爬取积分榜
        FBref数据更完整，反爬较少
        """
        league_urls = {
            'Premier League': 'https://fbref.com/en/comps/9/Premier-League-Stats',
            'La Liga': 'https://fbref.com/en/comps/12/La-Liga-Stats',
            'Serie A': 'https://fbref.com/en/comps/11/Serie-A-Stats',
            'Bundesliga': 'https://fbref.com/en/comps/20/Bundesliga-Stats',
        }

        url = league_urls.get(league)
        if not url:
            print(f"League {league} not supported")
            return []

        try:
            print(f"Fetching standings from FBref: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 查找积分榜表格
            table = soup.find('table', id='results2024-20251_overall')
            if not table:
                table = soup.find('table', {'class': 'stats_table'})

            if not table:
                print("Table not found")
                return []

            standings = []
            tbody = table.find('tbody')
            if not tbody:
                tbody = table

            rows = tbody.find_all('tr')
            for row in rows:
                try:
                    # 提取排名
                    rank_elem = row.find('th', {'data-stat': 'rank'})
                    if rank_elem:
                        position = int(rank_elem.text.strip())
                    else:
                        continue

                    # 提取球队名
                    team_elem = row.find('td', {'data-stat': 'team'})
                    if not team_elem:
                        continue

                    team_link = team_elem.find('a')
                    team_name = team_link.text.strip() if team_link else team_elem.text.strip()

                    # 提取积分、胜平负
                    points = int(row.find('td', {'data-stat': 'points'}).text.strip()) if row.find('td', {'data-stat': 'points'}) else 0
                    wins = int(row.find('td', {'data-stat': 'wins'}).text.strip()) if row.find('td', {'data-stat': 'wins'}) else 0
                    draws = int(row.find('td', {'data-stat': 'draws'}).text.strip()) if row.find('td', {'data-stat': 'draws'}) else 0
                    losses = int(row.find('td', {'data-stat': 'losses'}).text.strip()) if row.find('td', {'data-stat': 'losses'}) else 0

                    # 提取进球/失球
                    goals_for = int(row.find('td', {'data-stat': 'goals_for'}).text.strip()) if row.find('td', {'data-stat': 'goals_for'}) else 0
                    goals_against = int(row.find('td', {'data-stat': 'goals_against'}).text.strip()) if row.find('td', {'data-stat': 'goals_against'}) else 0

                    standings.append({
                        'position': position,
                        'team': team_name,
                        'points': points,
                        'wins': wins,
                        'draws': draws,
                        'losses': losses,
                        'goals_for': goals_for,
                        'goals_against': goals_against,
                        'goal_diff': goals_for - goals_against
                    })

                    if position >= 20:  # 只取前20名
                        break

                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue

            print(f"Successfully scraped {len(standings)} teams")
            return standings

        except Exception as e:
            print(f"Error scraping FBref: {e}")
            return []

    def get_team_form_from_fbref(self, team_name: str, league: str) -> List[str]:
        """
        从FBref获取球队近期状态
        """
        # 先找到球队页面
        search_url = f"https://fbref.com/en/search/search.fcgi?search={team_name}"

        try:
            response = self.session.get(search_url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 查找搜索结果
            search_results = soup.find('div', class_='search-item')
            if search_results:
                team_link = search_results.find('a')
                if team_link:
                    team_url = f"https://fbref.com{team_link['href']}"

                    # 获取球队页面
                    response = self.session.get(team_url, timeout=15)
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # 查找近期比赛
                    form = []
                    recent_games = soup.find_all('td', {'data-stat': 'result'})
                    for game in recent_games[-5:]:  # 最近5场
                        result = game.text.strip().upper()
                        if result in ['W', 'D', 'L']:
                            form.append(result)

                    return form

        except Exception as e:
            print(f"Error getting form: {e}")

        return []

    def get_h2h_from_api(self, home_team: str, away_team: str) -> List[Dict]:
        """
        使用API-Football的免费endpoint获取H2H
        注意：某些endpoint可能免费
        """
        # 备用方案：使用football-data.org (部分免费)
        url = f"https://www.football-data.org/teams/search/{home_team}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 解析数据...
        except:
            pass

        return []

    def get_standings_from_csv(self, league: str) -> List[Dict]:
        """
        从football-data.co.uk下载CSV格式的积分榜
        这个数据源完全免费，无需API key
        """
        # CSV文件URL映射
        csv_urls = {
            'Premier League': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
            'La Liga': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
            'Serie A': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
            'Bundesliga': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
        }

        url = csv_urls.get(league)
        if not url:
            print(f"League {league} not found in CSV sources")
            return []

        try:
            print(f"Downloading CSV from: {url}")
            response = self.session.get(url, timeout=20)
            response.raise_for_status()

            # 解析CSV
            import csv
            from io import StringIO

            csv_data = csv.DictReader(StringIO(response.text))

            # 统计积分榜
            standings_dict = {}

            for row in csv_data:
                home_team = row.get('HomeTeam', '')
                away_team = row.get('AwayTeam', '')
                fthg = row.get('FTHG', '0')  # Full Time Home Goals
                ftag = row.get('FTAG', '0')  # Full Time Away Goals
                ftr = row.get('FTR', '')     # Full Time Result (H/D/A)

                try:
                    home_goals = int(fthg)
                    away_goals = int(ftag)
                except:
                    continue

                # 更新主队统计
                if home_team not in standings_dict:
                    standings_dict[home_team] = {
                        'team': home_team,
                        'played': 0,
                        'wins': 0,
                        'draws': 0,
                        'losses': 0,
                        'goals_for': 0,
                        'goals_against': 0,
                        'points': 0
                    }

                # 更新客队统计
                if away_team not in standings_dict:
                    standings_dict[away_team] = {
                        'team': away_team,
                        'played': 0,
                        'wins': 0,
                        'draws': 0,
                        'losses': 0,
                        'goals_for': 0,
                        'goals_against': 0,
                        'points': 0
                    }

                # 更新比赛数据
                standings_dict[home_team]['played'] += 1
                standings_dict[away_team]['played'] += 1
                standings_dict[home_team]['goals_for'] += home_goals
                standings_dict[home_team]['goals_against'] += away_goals
                standings_dict[away_team]['goals_for'] += away_goals
                standings_dict[away_team]['goals_against'] += home_goals

                # 更新胜负平
                if ftr == 'H':
                    standings_dict[home_team]['wins'] += 1
                    standings_dict[home_team]['points'] += 3
                    standings_dict[away_team]['losses'] += 1
                elif ftr == 'D':
                    standings_dict[home_team]['draws'] += 1
                    standings_dict[home_team]['points'] += 1
                    standings_dict[away_team]['draws'] += 1
                    standings_dict[away_team]['points'] += 1
                elif ftr == 'A':
                    standings_dict[home_team]['losses'] += 1
                    standings_dict[away_team]['wins'] += 1
                    standings_dict[away_team]['points'] += 3

            # 转换为列表并排序
            standings = list(standings_dict.values())
            standings.sort(key=lambda x: (x['points'], x['goals_for'] - x['goals_against']), reverse=True)

            # 添加排名
            for i, team in enumerate(standings, 1):
                team['position'] = i

            print(f"Successfully loaded {len(standings)} teams from CSV")
            return standings

        except Exception as e:
            print(f"Error downloading CSV: {e}")
            return []

    def get_complete_match_data(self, home_team: str, away_team: str,
                                 league: str) -> Dict:
        """
        获取完整的比赛数据（整合多个来源）
        """
        # 标准化球队名称
        home_team_normalized = self.normalize_team_name(home_team)
        away_team_normalized = self.normalize_team_name(away_team)

        print(f"\nFetching complete match data: {home_team} vs {away_team}")
        if home_team != home_team_normalized or away_team != away_team_normalized:
            print(f"  Normalized names: {home_team_normalized} vs {away_team_normalized}")

        result = {
            'home_team': home_team,
            'away_team': away_team,
            'home_team_normalized': home_team_normalized,
            'away_team_normalized': away_team_normalized,
            'league': league,
            'timestamp': datetime.now().isoformat()
        }

        # 1. 获取积分榜
        print("Step 1: Fetching standings...")
        standings = self.get_standings_from_csv(league)
        if standings:
            result['standings'] = standings

            # 使用标准化后的名称查找排名
            home_pos = next((s['position'] for s in standings if s['team'] == home_team_normalized), None)
            away_pos = next((s['position'] for s in standings if s['team'] == away_team_normalized), None)

            result['home_league_position'] = home_pos
            result['away_league_position'] = away_pos
            print(f"  Home position: {home_pos}, Away position: {away_pos}")
        else:
            # 备用：尝试FBref
            standings = self.get_standings_from_fbref(league)
            if standings:
                result['standings'] = standings
                home_pos = next((s['position'] for s in standings if s['team'] == home_team), None)
                away_pos = next((s['position'] for s in standings if s['team'] == away_team), None)
                result['home_league_position'] = home_pos
                result['away_league_position'] = away_pos

        # 2. 获取近期状态（从CSV中的最近比赛提取）
        print("Step 2: Calculating form from recent matches...")
        home_form, away_form = self._calculate_form_from_csv(home_team_normalized, away_team_normalized, league)
        result['home_form'] = home_form
        result['away_form'] = away_form
        print(f"  Home form: {home_form}")
        print(f"  Away form: {away_form}")

        # 3. 生成默认伤停（因为免费API不提供）
        result['home_injuries'] = []
        result['away_injuries'] = []
        print("Step 3: Injuries not available in free sources")

        # 4. 从积分榜推断主客场战绩
        print("Step 4: Calculating home/away records...")
        home_home_record, away_away_record = self._calculate_home_away_records(home_team_normalized, away_team_normalized, league)
        result['home_home_record'] = home_home_record
        result['away_away_record'] = away_away_record
        print(f"  Home home record: {home_home_record}")
        print(f"  Away away record: {away_away_record}")

        return result

    def _calculate_form_from_csv(self, home_team: str, away_team: str,
                                  league: str) -> tuple:
        """从CSV数据计算近期状态"""
        csv_urls = {
            'Premier League': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
            'La Liga': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
            'Serie A': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
            'Bundesliga': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
            'Ligue 1': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
        }

        url = csv_urls.get(league)
        if not url:
            return [], []

        try:
            response = self.session.get(url, timeout=20)
            import csv
            from io import StringIO

            csv_data = list(csv.DictReader(StringIO(response.text)))

            # 提取最近比赛（倒序，从最新到最旧）
            recent_matches = list(reversed(csv_data))  # 真正的倒序

            home_form = []
            away_form = []

            # 查找主队最近5场
            for match in recent_matches:
                if len(home_form) >= 5:
                    break
                if match.get('HomeTeam') == home_team:
                    result = match.get('FTR', '')
                    if result == 'H':
                        home_form.append('W')
                    elif result == 'D':
                        home_form.append('D')
                    else:
                        home_form.append('L')
                elif match.get('AwayTeam') == home_team:
                    result = match.get('FTR', '')
                    if result == 'A':
                        home_form.append('W')
                    elif result == 'D':
                        home_form.append('D')
                    else:
                        home_form.append('L')

            # 查找客队最近5场
            for match in recent_matches:
                if len(away_form) >= 5:
                    break
                if match.get('HomeTeam') == away_team:
                    result = match.get('FTR', '')
                    if result == 'H':
                        away_form.append('W')
                    elif result == 'D':
                        away_form.append('D')
                    else:
                        away_form.append('L')
                elif match.get('AwayTeam') == away_team:
                    result = match.get('FTR', '')
                    if result == 'A':
                        away_form.append('W')
                    elif result == 'D':
                        away_form.append('D')
                    else:
                        away_form.append('L')

            return home_form[:5], away_form[:5]

        except Exception as e:
            print(f"Error calculating form: {e}")
            return [], []

    def _calculate_home_away_records(self, home_team: str, away_team: str,
                                      league: str) -> tuple:
        """从CSV数据计算主客场战绩"""
        csv_urls = {
            'Premier League': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
            'La Liga': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
            'Serie A': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
            'Bundesliga': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
            'Ligue 1': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
        }

        url = csv_urls.get(league)
        if not url:
            return {}, {}

        try:
            response = self.session.get(url, timeout=20)
            import csv
            from io import StringIO

            csv_data = csv.DictReader(StringIO(response.text))

            home_wins = home_draws = home_losses = 0
            away_wins = away_draws = away_losses = 0

            for match in csv_data:
                # 主队主场战绩
                if match.get('HomeTeam') == home_team:
                    result = match.get('FTR', '')
                    if result == 'H':
                        home_wins += 1
                    elif result == 'D':
                        home_draws += 1
                    else:
                        home_losses += 1

                # 客队客场战绩
                if match.get('AwayTeam') == away_team:
                    result = match.get('FTR', '')
                    if result == 'A':
                        away_wins += 1
                    elif result == 'D':
                        away_draws += 1
                    else:
                        away_losses += 1

            home_record = {
                'wins': home_wins,
                'draws': home_draws,
                'losses': home_losses
            }

            away_record = {
                'wins': away_wins,
                'draws': away_draws,
                'losses': away_losses
            }

            return home_record, away_record

        except Exception as e:
            print(f"Error calculating home/away records: {e}")
            return {}, {}


# 测试
def test_robust_scraper():
    """测试增强版爬虫"""
    print("=" * 60)
    print("增强版足球数据爬虫测试")
    print("=" * 60)

    scraper = RobustFootballScraper()

    # 测试1: 从CSV获取英超积分榜
    print("\n测试1: 从CSV获取英超积分榜...")
    standings = scraper.get_standings_from_csv('Premier League')
    print(f"积分榜 (前5名):")
    for team in standings[:5]:
        print(f"  {team['position']}. {team['team']} - {team['points']}分 ({team['wins']}-{team['draws']}-{team['losses']})")

    # 测试2: 获取完整比赛数据
    print("\n\n测试2: 获取完整比赛数据...")
    data = scraper.get_complete_match_data(
        home_team='Arsenal',
        away_team='Chelsea',
        league='Premier League'
    )

    print(f"\n结果摘要:")
    print(f"  主队排名: {data.get('home_league_position')}")
    print(f"  客队排名: {data.get('away_league_position')}")
    print(f"  主队近期状态: {data.get('home_form')}")
    print(f"  客队近期状态: {data.get('away_form')}")
    print(f"  主队主场战绩: {data.get('home_home_record')}")
    print(f"  客队客场战绩: {data.get('away_away_record')}")

    # 保存结果到JSON
    print("\n保存结果到JSON...")
    with open('scraper_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("已保存到 scraper_test_result.json")


if __name__ == '__main__':
    test_robust_scraper()
