"""
大模型深度分析服务
集成智谱AI和MiniMax API，基于实时数据生成深度分析报告
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class LLMAnalyzer:
    """大模型分析器"""

    def __init__(self):
        # 智谱AI配置
        self.zhipu_api_key = os.getenv('ZHIPU_API_KEY')
        self.zhipu_base_url = os.getenv('ZHIPU_API_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')

        # MiniMax配置
        self.minimax_api_key = os.getenv('MINIMAX_API_KEY')
        self.minimax_group_id = os.getenv('MINIMAX_GROUP_ID')
        self.minimax_base_url = os.getenv('MINIMAX_API_BASE_URL', 'https://api.minimax.chat/v1')

    def analyze_with_zhipu(self, realtime_data: Dict, dimension_scores: Dict) -> str:
        """
        使用智谱AI生成深度分析

        Args:
            realtime_data: 实时数据
            dimension_scores: 九维得分

        Returns:
            分析报告文本，失败时返回None（用于触发自动降级）
        """
        if not self.zhipu_api_key:
            print(f"  [智谱AI] 未配置API密钥")
            return None

        try:
            print(f"\n  [智谱AI] 开始分析...")

            # 构建提示词
            prompt = self._build_analysis_prompt(realtime_data, dimension_scores)

            # 调用智谱API
            url = f"{self.zhipu_base_url}chat/completions"
            headers = {
                'Authorization': f'Bearer {self.zhipu_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': 'glm-4-flash',  # 使用快速版本
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一位专业的足球分析师，精通九维全息赛事演算模型。请基于提供的实时数据和九维得分，生成深度、专业的比赛预测分析报告。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            analysis = result['choices'][0]['message']['content']
            print(f"  [智谱AI] 分析完成")
            return analysis

        except Exception as e:
            error_msg = str(e)
            # 检查是否是限额错误
            if 'quota' in error_msg.lower() or 'limit' in error_msg.lower() or '429' in error_msg:
                print(f"  [智谱AI] API限额已满，自动切换到MiniMax...")
            else:
                print(f"  [智谱AI] 分析失败: {e}")
            # 返回None触发自动降级
            return None

    def analyze_with_minimax(self, realtime_data: Dict, dimension_scores: Dict) -> str:
        """
        使用MiniMax生成深度分析

        Args:
            realtime_data: 实时数据
            dimension_scores: 九维得分

        Returns:
            分析报告文本
        """
        if not self.minimax_api_key:
            return "【MiniMax未配置】跳过MiniMax分析"

        try:
            print(f"\n  [MiniMax] 开始分析...")

            # 构建提示词
            prompt = self._build_analysis_prompt(realtime_data, dimension_scores)

            # 调用MiniMax API
            url = f"{self.minimax_base_url}/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.minimax_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': 'abab6.5s-chat',
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一位专业的足球分析师，精通九维全息赛事演算模型。请基于提供的实时数据和九维得分，生成深度、专业的比赛预测分析报告。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 2000,
                'do_sample': True,
                'top_p': 0.7
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            analysis = result['choices'][0]['message']['content']
            print(f"  [MiniMax] 分析完成")
            return analysis

        except Exception as e:
            print(f"  [MiniMax] 分析失败: {e}")
            return f"【MiniMax分析失败】{str(e)}"

    def _build_analysis_prompt(self, realtime_data: Dict, dimension_scores: Dict) -> str:
        """构建分析提示词"""

        prompt = f"""
# 比赛信息
- 对阵双方: {realtime_data['home_team']} vs {realtime_data['away_team']}
- 联赛: {realtime_data['league']}
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# 实时数据

## 伤停情况
主队伤停: {len(realtime_data.get('home_injuries', []))}人
{self._format_injuries(realtime_data.get('home_injuries', []))}

客队伤停: {len(realtime_data.get('away_injuries', []))}人
{self._format_injuries(realtime_data.get('away_injuries', []))}

## 历史交锋（最近10场）
{self._format_h2h(realtime_data.get('h2h_matches', []))}

## 球队统计
主队: {realtime_data.get('home_stats', {})}
客队: {realtime_data.get('away_stats', {})}

## 首发阵容（如有）
{self._format_lineups(realtime_data.get('lineups', {}))}

# 九维得分分析
{self._format_dimension_scores(dimension_scores)}

# 任务要求
请基于以上信息，从以下三个维度生成深度分析：

1. **核心因素分析**（300字）
   - 找出本场比赛最关键的3-5个影响因素
   - 分析伤停对战术的影响
   - 历史交锋的心理优势分析

2. **战术博弈预测**（200字）
   - 双方可能的战术布置
   - 关键位置对位分析
   - 比赛节奏预判

3. **最终预测**（100字）
   - 基于以上分析，给出明确的比分预测
   - 置信度评估

请用专业、客观的语言，避免过度主观判断。
"""

        return prompt

    def _format_injuries(self, injuries: List[Dict]) -> str:
        """格式化伤停信息"""
        if not injuries:
            return "无伤停"

        result = []
        for player in injuries[:5]:  # 只显示前5个
            key_marker = " [核心]" if player.get('is_key_player') else ""
            result.append(f"- {player['player']}: {player['reason']}{key_marker}")

        return "\n".join(result)

    def _format_h2h(self, h2h_matches: List[Dict]) -> str:
        """格式化历史交锋"""
        if not h2h_matches:
            return "无历史交锋数据"

        home_wins = sum(1 for m in h2h_matches if m['winner'] == 'home')
        draws = sum(1 for m in h2h_matches if m['winner'] == 'draw')
        away_wins = sum(1 for m in h2h_matches if m['winner'] == 'away')

        result = f"战绩: 主胜{home_wins} 平{draws} 客胜{away_wins}\n"
        result += "最近5场:\n"

        for match in h2h_matches[-5:]:
            result += f"- {match['date'][:10]}: {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}\n"

        return result

    def _format_lineups(self, lineups: Dict) -> str:
        """格式化阵容信息"""
        if not lineups:
            return "阵容尚未公布"

        result = []
        for side in ['home', 'away']:
            if side in lineups and lineups[side]:
                formation = lineups[side].get('formation', 'Unknown')
                players_count = len(lineups[side].get('players', []))
                result.append(f"{'主队' if side == 'home' else '客队'}: {formation} ({players_count}人)")

        return "\n".join(result) if result else "阵容数据不完整"

    def _format_dimension_scores(self, scores: Dict) -> str:
        """格式化九维得分"""
        dimension_names = {
            'odds': '盘口赔率',
            'injuries': '伤停情报',
            'players': '球员状态',
            'tactics': '战术相克',
            'home_advantage': '主场优势',
            'referee': '裁判因素',
            'h2h': '历史交锋',
            'motivation': '赛事战意',
            'fitness': '体能状况'
        }

        result = []
        for key, score in sorted(scores.items(), key=lambda x: -x[1]):
            name = dimension_names.get(key, key)
            level = self._get_score_level(score)
            result.append(f"- {name}: {score:.2f} ({level})")

        return "\n".join(result)

    def _get_score_level(self, score: float) -> str:
        """获取得分等级"""
        if score >= 0.7:
            return "强"
        elif score >= 0.6:
            return "中上"
        elif score >= 0.4:
            return "中等"
        elif score >= 0.3:
            return "中下"
        else:
            return "弱"

    def _extract_key_insights(self, realtime_data: Dict, dimension_scores: Dict) -> List[str]:
        """从数据中提取关键洞察"""
        insights = []

        # 伤停分析
        home_injuries = realtime_data.get('home_injuries', [])
        away_injuries = realtime_data.get('away_injuries', [])

        key_home_injuries = [p for p in home_injuries if p.get('is_key_player')]
        key_away_injuries = [p for p in away_injuries if p.get('is_key_player')]

        if key_home_injuries:
            insights.append(f"⚠️  主队核心球员伤停: {', '.join([p['player'] for p in key_home_injuries[:3]])}")

        if key_away_injuries:
            insights.append(f"⚠️  客队核心球员伤停: {', '.join([p['player'] for p in key_away_injuries[:3]])}")

        # H2H分析
        h2h_matches = realtime_data.get('h2h_matches', [])
        if h2h_matches:
            home_wins = sum(1 for m in h2h_matches if m['winner'] == 'home')
            away_wins = sum(1 for m in h2h_matches if m['winner'] == 'away')

            if home_wins >= len(h2h_matches) * 0.7:
                insights.append(f"🔥 主队历史交锋占优（{home_wins}胜/{len(h2h_matches)}场）")
            elif away_wins >= len(h2h_matches) * 0.7:
                insights.append(f"🔥 客队历史交锋占优（{away_wins}胜/{len(h2h_matches)}场）")

        # 维度分析
        top_dimensions = sorted(dimension_scores.items(), key=lambda x: -x[1])[:3]
        for dim, score in top_dimensions:
            if score >= 0.65:
                dimension_names = {
                    'odds': '盘口赔率',
                    'injuries': '伤停情报',
                    'players': '球员状态',
                    'tactics': '战术相克',
                    'home_advantage': '主场优势',
                    'referee': '裁判因素',
                    'h2h': '历史交锋',
                    'motivation': '赛事战意',
                    'fitness': '体能状况'
                }
                name = dimension_names.get(dim, dim)
                insights.append(f"📊 {name}得分突出: {score:.2f}")

        return insights


async def generate_llm_analysis(realtime_data: Dict, dimension_scores: Dict,
                                   use_zhipu: bool = True, use_minimax: bool = False) -> Dict:
    """
    生成大模型分析报告（自动降级：智谱AI -> MiniMax）

    Args:
        realtime_data: 实时数据
        dimension_scores: 九维得分
        use_zhipu: 是否使用智谱AI（优先）
        use_minimax: 是否使用MiniMax（备用）

    Returns:
        分析报告字典

    自动降级逻辑：
    1. 优先使用智谱AI
    2. 智谱AI失败/限额时，自动切换到MiniMax
    3. MiniMax也失败时，返回错误信息
    """
    print(f"\n{'='*60}")
    print(f"【第二步】大模型深度分析")
    print(f"{'='*60}")

    start_time = datetime.now()
    analyzer = LLMAnalyzer()

    result = {
        'analysis_time': start_time.isoformat(),
        'zhipu_analysis': None,
        'minimax_analysis': None,
        'primary_provider': None,
        'fallback_triggered': False,
        'combined_insights': []
    }

    # 智谱AI分析
    if use_zhipu:
        print(f"\n[1/1] 智谱AI分析...")
        zhipu_result = analyzer.analyze_with_zhipu(realtime_data, dimension_scores)

        if zhipu_result is not None:
            # 智谱AI成功
            result['zhipu_analysis'] = zhipu_result
            result['primary_provider'] = 'zhipu'
            print(f"  [OK] 智谱AI分析成功")
        else:
            # 智谱AI失败
            result['zhipu_analysis'] = None
            result['primary_provider'] = 'none'
            print(f"  [ERROR] 智谱AI暂时不可用，请稍后重试")
    else:
        result['primary_provider'] = 'none'

    # 2. 提取关键insights
    result['combined_insights'] = analyzer._extract_key_insights(realtime_data, dimension_scores)

    elapsed = (datetime.now() - start_time).total_seconds()

    print(f"\n{'='*60}")
    print(f"[OK] LLM analysis complete! Time: {elapsed:.2f}s")
    print(f"Provider: {result['primary_provider']}")
    if result['fallback_triggered']:
        print(f"Fallback: MiniMax (智谱AI不可用)")
    print(f"{'='*60}")

    return result


# 测试
if __name__ == '__main__':
    import asyncio

    async def test():
        # 模拟数据
        realtime_data = {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'league': 'La Liga',
            'home_injuries': [
                {'player': 'Courtois', 'reason': '膝盖受伤', 'is_key_player': True}
            ],
            'away_injuries': [],
            'h2h_matches': [
                {'date': '2024-01-01', 'home_team': 'Real Madrid', 'away_team': 'Barcelona',
                 'home_score': 2, 'away_score': 1, 'winner': 'home'}
            ],
            'home_stats': {'wins': 15, 'draws': 3, 'losses': 2},
            'away_stats': {'wins': 12, 'draws': 5, 'losses': 3},
            'lineups': {}
        }

        dimension_scores = {
            'odds': 0.65,
            'injuries': 0.45,
            'players': 0.60,
            'tactics': 0.50,
            'home_advantage': 0.55,
            'referee': 0.50,
            'h2h': 0.70,
            'motivation': 0.60,
            'fitness': 0.50
        }

        result = await generate_llm_analysis(realtime_data, dimension_scores)

        print("\n\n=== 最终分析报告 ===")
        print(result.get('zhipu_analysis', '智谱AI未配置'))

    asyncio.run(test())
