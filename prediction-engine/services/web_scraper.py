"""
足球数据爬虫
从公开网站爬取：积分榜、历史交锋、伤停、近期状态
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from urllib.parse import urljoin


class FootballScraper:
    """足球数据爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

        # 基础URL
        self.base_url = "https://www.flashscore.com"

        # 延迟设置（避免被封）
        self.min_delay = 2
        self.max_delay = 5

    def _random_delay(self):
        """随机延迟"""
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)

    def _get_page(self, url: str) -> Optional[str]:
        """获取网页内容"""
        try:
            self._random_delay()
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: Status {response.status_code} for URL: {url}")
        except Exception as e:
            print(f"Error fetching {url}: {e}")

        return None

    def search_team(self, team_name: str) -> Optional[str]:
        """
        搜索球队，返回球队URL
        """
        try:
            # 使用Flashscore搜索
            search_url = f"{self.base_url}/search/?q={team_name}"
            html = self._get_page(search_url)

            if html:
                soup = BeautifulSoup(html, 'html.parser')

                # 查找搜索结果
                search_results = soup.find('div', class_='search__results')
                if search_results:
                    # 查找球队链接
                    team_links = search_results.find_all('a', href=re.compile(r'/team/'))
                    if team_links:
                        team_url = urljoin(self.base_url, team_links[0]['href'])
                        print(f"Found team: {team_name} -> {team_url}")
                        return team_url
        except Exception as e:
            print(f"Error searching team {team_name}: {e}")

        return None

    def get_team_standings(self, team_url: str) -> Optional[Dict]:
        """
        获取球队在联赛中的排名
        """
        try:
            html = self._get_page(team_url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')

            # 查找联赛排名信息
            # Flashscore的球队页面会显示当前联赛排名
            standings_section = soup.find('div', class_='team__standings')
            if standings_section:
                # 提取排名
                position_elem = standings_section.find('span', class_='team__standings__pos')
                if position_elem:
                    position = int(position_elem.text.strip())

                    # 提取积分
                    points_elem = standings_section.find('span', class_='team__standings__pts')
                    points = int(points_elem.text.strip()) if points_elem else 0

                    # 提取联赛名称
                    league_elem = standings_section.find('a', class_='team__standings__league')
                    league = league_elem.text.strip() if league_elem else 'Unknown'

                    return {
                        'position': position,
                        'points': points,
                        'league': league
                    }

            # 备用方案：从页面其他位置提取
            # 查找表格中的排名数据
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 2:
                        # 第一列可能是排名
                        try:
                            pos_text = cells[0].text.strip()
                            if pos_text.isdigit():
                                return {'position': int(pos_text)}
                        except:
                            continue

        except Exception as e:
            print(f"Error getting standings: {e}")

        return None

    def get_team_form(self, team_url: str, last_n: int = 5) -> List[str]:
        """
        获取球队近期状态
        返回：['W', 'D', 'L', 'W', 'W']
        """
        try:
            html = self._get_page(team_url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')

            # 查找近期状态
            # Flashscore通常在球队页面显示最近的比赛结果
            form_section = soup.find('div', class_='form__')
            if form_section:
                form_spans = form_section.find_all('span')
                form = []
                for span in form_spans[:last_n]:
                    text = span.text.strip().upper()
                    if text in ['W', 'D', 'L']:
                        form.append(text)
                return form

            # 备用方案：从最近的比赛中提取
            matches_section = soup.find('div', id='tab-team-results')
            if matches_section:
                matches = matches_section.find_all('tr', class_='highlight')
                form = []
                for match in matches[:last_n]:
                    # 查找胜负结果
                    result_elem = match.find('span', class_='form')
                    if result_elem:
                        text = result_elem.text.strip().upper()
                        if text in ['W', 'D', 'L']:
                            form.append(text)
                return form

        except Exception as e:
            print(f"Error getting team form: {e}")

        return []

    def get_h2h(self, home_team: str, away_team: str) -> List[Dict]:
        """
        获取两队历史交锋
        """
        try:
            # 构建H2H搜索URL
            # Flashscore格式: /h2h/队1/队2/
            home_slug = home_name_to_slug(home_team)
            away_slug = home_name_to_slug(away_team)
            h2h_url = f"{self.base_url}/h2h/{home_slug}/{away_slug}/"

            html = self._get_page(h2h_url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')

            # 查找历史交锋表格
            h2h_section = soup.find('div', id='tab-h2h')
            if not h2h_section:
                return []

            matches = []
            rows = h2h_section.find_all('tr', class_='highlight')

            for row in rows[:10]:  # 最近10场
                try:
                    # 提取日期
                    date_elem = row.find('td', class_='time')
                    date_str = date_elem.text.strip() if date_elem else ''

                    # 提取比分
                    score_elem = row.find('span', class_='score')
                    if score_elem:
                        score_text = score_elem.text.strip()
                        if ':' in score_text:
                            home_score, away_score = map(int, score_text.split(':'))
                        else:
                            home_score = away_score = 0
                    else:
                        home_score = away_score = 0

                    # 提取主客队
                    home_elem = row.find('span', class_='home')
                    away_elem = row.find('span', class_='away')

                    home_name = home_elem.text.strip() if home_elem else home_team
                    away_name = away_elem.text.strip() if away_elem else away_team

                    # 判断胜者
                    if home_score > away_score:
                        winner = 'home'
                    elif home_score < away_score:
                        winner = 'away'
                    else:
                        winner = 'draw'

                    matches.append({
                        'date': date_str,
                        'home_team': home_name,
                        'away_team': away_name,
                        'home_score': home_score,
                        'away_score': away_score,
                        'winner': winner
                    })

                except Exception as e:
                    print(f"Error parsing H2H row: {e}")
                    continue

            return matches

        except Exception as e:
            print(f"Error getting H2H: {e}")

        return []

    def get_injuries(self, team_name: str) -> List[Dict]:
        """
        获取球队伤停信息
        注意：Flashscore的伤停信息可能在单独的页面
        """
        try:
            # 先搜索球队
            team_url = self.search_team(team_name)
            if not team_url:
                return []

            # 查找球队页面的伤停/阵容信息
            html = self._get_page(team_url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')

            injuries = []

            # 查找伤停section
            squad_section = soup.find('div', id='tab-squad')
            if squad_section:
                # 查找受伤球员
                player_rows = squad_section.find_all('tr', class_='injured')
                for row in player_rows:
                    try:
                        # 提取球员信息
                        name_elem = row.find('td', class_='name')
                        name = name_elem.text.strip() if name_elem else 'Unknown'

                        # 提取位置
                        pos_elem = row.find('td', class_='pos')
                        position = pos_elem.text.strip() if pos_elem else 'Unknown'

                        # 提取伤停原因
                        reason_elem = row.find('td', class_='reason')
                        reason = reason_elem.text.strip() if reason_elem else 'Injured'

                        injuries.append({
                            'name': name,
                            'position': position,
                            'reason': reason,
                            'type': 'injury'
                        })

                    except Exception as e:
                        print(f"Error parsing injury row: {e}")
                        continue

            return injuries

        except Exception as e:
            print(f"Error getting injuries: {e}")

        return []

    def get_match_preview(self, home_team: str, away_team: str) -> Dict:
        """
        获取比赛预览信息
        包括：主客场战绩、近期状态、历史交锋等
        """
        try:
            # 构建比赛页面URL
            home_slug = home_name_to_slug(home_team)
            away_slug = home_name_to_slug(away_team)
            match_url = f"{self.base_url}/match/{home_slug}-{away_slug}/"

            html = self._get_page(match_url)
            if not html:
                return {}

            soup = BeautifulSoup(html, 'html.parser')

            preview = {}

            # 提取主队主场战绩
            home_record_section = soup.find('div', class_='home-record')
            if home_record_section:
                preview['home_home_record'] = extract_record(home_record_section)

            # 提取客队客场战绩
            away_record_section = soup.find('div', class_='away-record')
            if away_record_section:
                preview['away_away_record'] = extract_record(away_record_section)

            # 提取裁判信息
            referee_section = soup.find('div', class_='referee')
            if referee_section:
                referee_name = referee_section.find('span', class_='name')
                preview['referee'] = {
                    'name': referee_name.text.strip() if referee_name else 'Unknown'
                }

            return preview

        except Exception as e:
            print(f"Error getting match preview: {e}")

        return {}


# 辅助函数
def home_name_to_slug(team_name: str) -> str:
    """将球队名称转换为URL slug"""
    # 简单实现：转小写，替换空格为连字符
    slug = team_name.lower().replace(' ', '-').replace('/', '-')
    # 移除特殊字符
    slug = re.sub(r'[^\w\-]', '', slug)
    return slug


def extract_record(element) -> Dict:
    """从HTML元素提取战绩"""
    try:
        stats = element.find_all('span')
        if len(stats) >= 3:
            wins = int(stats[0].text.strip())
            draws = int(stats[1].text.strip())
            losses = int(stats[2].text.strip())
            return {
                'wins': wins,
                'draws': draws,
                'losses': losses
            }
    except:
        pass

    return {}


# 爬取特定联赛的积分榜
class StandingsScraper:
    """积分榜爬虫"""

    def __init__(self):
        self.scraper = FootballScraper()

    def get_premier_league_standings(self) -> List[Dict]:
        """获取英超积分榜"""
        url = "https://www.flashscore.com/england/premier-league/standings/"
        return self._parse_standings(url)

    def get_la_liga_standings(self) -> List[Dict]:
        """获取西甲积分榜"""
        url = "https://www.flashscore.com/spain/laliga/standings/"
        return self._parse_standings(url)

    def get_serie_a_standings(self) -> List[Dict]:
        """获取意甲积分榜"""
        url = "https://www.flashscore.com/italy/serie-a/standings/"
        return self._parse_standings(url)

    def _parse_standings(self, url: str) -> List[Dict]:
        """解析积分榜页面"""
        try:
            html = self.scraper._get_page(url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')

            standings = []

            # 查找积分榜表格
            table = soup.find('table', class_='standings')
            if table:
                rows = table.find_all('tr')[1:]  # 跳过表头

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 8:
                        # 提取球队信息
                        position = int(cells[0].text.strip()) if cells[0].text.strip().isdigit() else 0

                        team_elem = cells[1].find('a')
                        team_name = team_elem.text.strip() if team_elem else 'Unknown'

                        played = int(cells[2].text.strip()) if cells[2].text.strip().isdigit() else 0
                        wins = int(cells[3].text.strip()) if cells[3].text.strip().isdigit() else 0
                        draws = int(cells[4].text.strip()) if cells[4].text.strip().isdigit() else 0
                        losses = int(cells[5].text.strip()) if cells[5].text.strip().isdigit() else 0
                        points = int(cells[8].text.strip()) if len(cells) > 8 and cells[8].text.strip().isdigit() else 0

                        standings.append({
                            'position': position,
                            'team': team_name,
                            'played': played,
                            'wins': wins,
                            'draws': draws,
                            'losses': losses,
                            'points': points
                        })

            return standings

        except Exception as e:
            print(f"Error parsing standings: {e}")

        return []


# 测试
async def test_scraper():
    """测试爬虫"""
    print("=" * 60)
    print("足球数据爬虫测试")
    print("=" * 60)

    scraper = FootballScraper()

    # 测试1: 搜索球队
    print("\n测试1: 搜索球队...")
    team_url = scraper.search_team('Manchester United')
    if team_url:
        print(f"[OK] 找到球队URL: {team_url}")

        # 测试2: 获取排名
        print("\n测试2: 获取排名...")
        standings = scraper.get_team_standings(team_url)
        print(f"排名: {standings}")

        # 测试3: 获取近期状态
        print("\n测试3: 获取近期状态...")
        form = scraper.get_team_form(team_url)
        print(f"近期状态: {form}")

    # 测试4: 获取H2H
    print("\n测试4: 获取历史交锋...")
    h2h = scraper.get_h2h('Manchester United', 'Liverpool')
    print(f"历史交锋 ({len(h2h)} 场):")
    for match in h2h[:3]:
        print(f"  {match['date']}: {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")

    # 测试5: 获取伤停
    print("\n测试5: 获取伤停...")
    injuries = scraper.get_injuries('Manchester United')
    print(f"伤停: {len(injuries)} 人")
    for injury in injuries[:3]:
        print(f"  - {injury['name']} ({injury['position']}): {injury['reason']}")

    # 测试6: 获取英超积分榜
    print("\n测试6: 获取英超积分榜...")
    standings_scraper = StandingsScraper()
    pl_standings = standings_scraper.get_premier_league_standings()
    print(f"积分榜 (前5名):")
    for team in pl_standings[:5]:
        print(f"  {team['position']}. {team['team']} - {team['points']}分")


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_scraper())
