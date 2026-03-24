import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getTeamName } from '../utils/teamNames';

// API 配置 - 自动检测环境
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:5000'  // 本地环境
  : window.location.origin;  // 公网环境：使用当前域名（自动适配）

export default function PredictPage() {
  const navigate = useNavigate();

  // 表单状态
  const [selectedLeague, setSelectedLeague] = useState('all');
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [leagues, setLeagues] = useState([]);

  // 比赛数据
  const [allMatches, setAllMatches] = useState([]); // 所有比赛
  const [filteredMatches, setFilteredMatches] = useState([]); // 筛选后的比赛
  const [homeTeams, setHomeTeams] = useState([]); // 所有主队
  const [awayTeams, setAwayTeams] = useState([]); // 根据主队筛选的客队
  const [selectedMatch, setSelectedMatch] = useState(null);

  // 加载状态
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  // 预测倒计时状态
  const [remainingTime, setRemainingTime] = useState(0);
  const [estimatedTotalTime] = useState(45); // 预计45秒
  const [predictionProgress, setPredictionProgress] = useState(''); // 预测进度描述

  // 加载联赛列表和比赛数据
  useEffect(() => {
    fetchLeagues();
    fetchAllMatches();
  }, []);

  // 当联赛改变时，筛选比赛
  useEffect(() => {
    if (selectedLeague === 'all') {
      setFilteredMatches(allMatches);
    } else {
      // 根据联赛代码或名称筛选
      const filtered = allMatches.filter(m => {
        const leagueCode = m.league_code || '';
        const leagueName = m.league || '';
        return leagueCode === selectedLeague || leagueName.includes(selectedLeague);
      });
      setFilteredMatches(filtered);
    }

    // 重置球队选择
    setHomeTeam('');
    setAwayTeam('');
    setSelectedMatch(null);
    setPrediction(null);
  }, [selectedLeague, allMatches]);

  // 当筛选后的比赛改变时，更新球队列表
  useEffect(() => {
    const teams = [...new Set(filteredMatches.map(m => m.home_team))];
    setHomeTeams(teams);
    const allAway = [...new Set(filteredMatches.map(m => m.away_team))];
    setAwayTeams(allAway);
  }, [filteredMatches]);

  // 辅助函数：获取球队显示名称
  const getDisplayTeamName = (teamName) => {
    return getTeamName(teamName);
  };

  // 当主队改变时，更新客队列表
  useEffect(() => {
    if (homeTeam) {
      const opponentMatches = filteredMatches.filter(m => m.home_team === homeTeam);
      const opponents = [...new Set(opponentMatches.map(m => m.away_team))];
      setAwayTeams(opponents);
      if (!opponents.includes(awayTeam)) {
        setAwayTeam('');
      }
    } else {
      const allAwayTeams = [...new Set(filteredMatches.map(m => m.away_team))];
      setAwayTeams(allAwayTeams);
    }
  }, [homeTeam, filteredMatches]);

  const fetchLeagues = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/leagues`);
      const data = await response.json();
      if (data.success) {
        setLeagues(data.leagues);
      }
    } catch (error) {
      console.error('获取联赛列表失败:', error);
    }
  };

  const fetchAllMatches = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('[DEBUG] API_BASE_URL:', API_BASE_URL);
      console.log('[DEBUG] Fetching matches from', `${API_BASE_URL}/api/matches/today`);
      const response = await fetch(`${API_BASE_URL}/api/matches/today`);
      console.log('[DEBUG] Response status:', response.status);
      console.log('[DEBUG] Response ok:', response.ok);

      const data = await response.json();
      console.log('[DEBUG] Matches data:', data);
      console.log('[DEBUG] Matches count:', data.matches?.length);
      console.log('[DEBUG] First match:', data.matches?.[0]);

      // 检查每场比赛的赔率
      if (data.matches) {
        data.matches.forEach((m, i) => {
          if (m.home_odds === 1.01 && m.draw_odds === 1.01 && m.away_odds === 1.01) {
            console.error(`[ERROR] Match ${i} has all 1.01 odds:`, m);
          }
        });
      }

      if (data.success) {
        setAllMatches(data.matches);
        setFilteredMatches(data.matches);

        if (data.matches.length === 0) {
          setError('目前暂无比赛数据');
        }
      }
    } catch (error) {
      console.error('[ERROR] 获取比赛失败:', error);
      console.error('[ERROR] Error details:', {
        message: error.message,
        stack: error.stack
      });
      setError(`无法连接到后端服务: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // 根据主队和客队找到对应的比赛
  useEffect(() => {
    if (homeTeam && awayTeam) {
      const match = filteredMatches.find(m => m.home_team === homeTeam && m.away_team === awayTeam);
      if (match) {
        setSelectedMatch(match);
      } else {
        setSelectedMatch(null);
      }
    } else {
      setSelectedMatch(null);
    }
  }, [homeTeam, awayTeam, filteredMatches]);

  const handlePredict = async () => {
    if (!selectedMatch) {
      setError('请选择主队和客队');
      return;
    }

    setPredicting(true);
    setError(null);
    setRemainingTime(estimatedTotalTime);

    // 预测进度描述
    const progressSteps = [
      { time: 45, text: '正在获取实时数据...' },
      { time: 35, text: '正在计算九维分析...' },
      { time: 15, text: '正在生成 AI 深度分析...' },
      { time: 5, text: '正在整理预测结果...' },
    ];

    // 启动倒计时
    const timer = setInterval(() => {
      setRemainingTime(prev => {
        const newTime = prev - 1;

        // 更新进度描述
        const step = progressSteps.find(s => newTime <= s.time && newTime > s.time - 10);
        if (step) {
          setPredictionProgress(step.text);
        }

        if (newTime <= 0) {
          clearInterval(timer);
          return 0;
        }
        return newTime;
      });
    }, 1000);

    try {
      const response = await fetch(`${API_BASE_URL}/api/predictions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          home_team: selectedMatch.home_team,
          away_team: selectedMatch.away_team,
          league: selectedMatch.league || '英超',
          home_odds: selectedMatch.home_odds,
          draw_odds: selectedMatch.draw_odds,
          away_odds: selectedMatch.away_odds,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '预测失败');
      }

      setPrediction(data.prediction);
    } catch (err) {
      setError(err.message || '预测失败，请稍后重试');
    } finally {
      clearInterval(timer);
      setPredicting(false);
      setRemainingTime(0);
      setPredictionProgress('');
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '1000px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '36px', fontWeight: 'bold', marginBottom: '30px', textAlign: 'center' }}>
        🔮 足球比分预测 - 九维分析
      </h1>

      {/* 步骤1: 选择联赛 */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ fontSize: '24px', marginBottom: '20px', color: '#333' }}>
          第1步：选择联赛
        </h2>

        <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
              ⏳ 正在加载比赛数据...
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
                  ⚽ 选择联赛（共 {allMatches.length} 场比赛）
                </label>
                <select
                  value={selectedLeague}
                  onChange={(e) => setSelectedLeague(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    backgroundColor: 'white',
                  }}
                >
                  <option value="all">全部联赛 ({allMatches.length} 场)</option>
                  {leagues.map((league) => {
                    const count = allMatches.filter(m =>
                      (m.league_code === league.code) ||
                      (m.league && m.league.includes(league.name.split(' ')[0]))
                    ).length;
                    if (count > 0) {
                      return (
                        <option key={league.code} value={league.code}>
                          {league.name} ({count} 场)
                        </option>
                      );
                    }
                    return null;
                  })}
                </select>
              </div>

              {selectedLeague !== 'all' && (
                <div style={{ fontSize: '14px', color: '#666' }}>
                  当前显示：{leagues.find(l => l.code === selectedLeague)?.name} - {filteredMatches.length} 场比赛
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* 步骤2: 选择球队 */}
      {!loading && filteredMatches.length > 0 && (
        <div style={{ marginBottom: '40px' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '20px', color: '#333' }}>
            第2步：选择球队
          </h2>

          <div style={{ backgroundColor: 'white', padding: '30px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            {/* 球队选择 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
              {/* 主队选择 */}
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
                  🏠 主队
                </label>
                <select
                  value={homeTeam}
                  onChange={(e) => setHomeTeam(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    backgroundColor: 'white',
                  }}
                >
                  <option value="">请选择主队</option>
                  {homeTeams.map((team) => (
                    <option key={team} value={team}>
                      {getDisplayTeamName(team)}
                    </option>
                  ))}
                </select>
              </div>

              {/* 客队选择 */}
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
                  ✈️ 客队
                </label>
                <select
                  value={awayTeam}
                  onChange={(e) => setAwayTeam(e.target.value)}
                  disabled={!homeTeam}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '16px',
                    backgroundColor: homeTeam ? 'white' : '#f3f4f6',
                    cursor: homeTeam ? 'pointer' : 'not-allowed',
                  }}
                >
                  <option value="">请选择客队</option>
                  {awayTeams.map((team) => (
                    <option key={team} value={team}>
                      {getDisplayTeamName(team)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* 显示选中的比赛信息 */}
            {selectedMatch && (
              <div style={{
                padding: '20px',
                backgroundColor: '#eff6ff',
                borderRadius: '8px',
                border: '2px solid #3b82f6',
              }}>
                <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '10px', textAlign: 'center' }}>
                  {getDisplayTeamName(selectedMatch.home_team)} vs {getDisplayTeamName(selectedMatch.away_team)}
                </div>
                <div style={{ textAlign: 'center', color: '#666', marginBottom: '10px' }}>
                  🏆 {selectedMatch.league}
                </div>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '30px', fontSize: '14px' }}>
                  <div>
                    <span style={{ color: '#999' }}>主胜：</span>
                    <span style={{ fontWeight: 'bold', color: '#16a34a', fontSize: '18px' }}>
                      {selectedMatch.home_odds}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#999' }}>平局：</span>
                    <span style={{ fontWeight: 'bold', fontSize: '18px' }}>
                      {selectedMatch.draw_odds}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#999' }}>客胜：</span>
                    <span style={{ fontWeight: 'bold', color: '#dc2626', fontSize: '18px' }}>
                      {selectedMatch.away_odds}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 步骤3: 生成预测 */}
      {selectedMatch && (
        <div style={{ marginBottom: '40px' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '20px', color: '#333' }}>
            第3步：生成九维预测
          </h2>

          <button
            onClick={handlePredict}
            disabled={predicting}
            style={{
              width: '100%',
              padding: '20px',
              fontSize: '18px',
              fontWeight: 'bold',
              backgroundColor: predicting ? '#999' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              cursor: predicting ? 'not-allowed' : 'pointer',
            }}
          >
            {predicting ? '⏳ 分析中...' : '🎯 生成九维预测'}
          </button>

          {/* 预测进度显示 */}
          {predicting && (
            <div style={{
              marginTop: '20px',
              padding: '20px',
              backgroundColor: '#f8fafc',
              borderRadius: '12px',
              border: '2px solid #e2e8f0',
            }}>
              {/* 倒计时 */}
              <div style={{ textAlign: 'center', marginBottom: '15px' }}>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                  预计剩余时间
                </div>
                <div style={{
                  fontSize: '36px',
                  fontWeight: 'bold',
                  color: remainingTime > 10 ? '#3b82f6' : remainingTime > 5 ? '#f59e0b' : '#ef4444',
                }}>
                  {remainingTime} 秒
                </div>
              </div>

              {/* 进度条 */}
              <div style={{ marginBottom: '15px' }}>
                <div style={{
                  height: '12px',
                  backgroundColor: '#e5e7eb',
                  borderRadius: '6px',
                  overflow: 'hidden',
                  marginBottom: '8px',
                }}>
                  <div style={{
                    height: '100%',
                    width: `${((estimatedTotalTime - remainingTime) / estimatedTotalTime) * 100}%`,
                    background: 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)',
                    transition: 'width 1s linear',
                    borderRadius: '6px',
                  }}></div>
                </div>
                <div style={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
                  {Math.round(((estimatedTotalTime - remainingTime) / estimatedTotalTime) * 100)}% 完成
                </div>
              </div>

              {/* 当前阶段 */}
              <div style={{
                padding: '12px',
                backgroundColor: 'white',
                borderRadius: '8px',
                textAlign: 'center',
                border: '1px solid #e2e8f0',
              }}>
                <div style={{ fontSize: '14px', color: '#333' }}>
                  {predictionProgress || '正在初始化...'}
                </div>
              </div>

              {/* 提示信息 */}
              <div style={{
                marginTop: '12px',
                fontSize: '12px',
                color: '#999',
                textAlign: 'center',
              }}>
                💡 完整预测需要 20-40 秒，包含九维分析和 AI 深度分析
              </div>
            </div>
          )}
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div style={{
          padding: '15px',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '8px',
          color: '#c33',
          marginBottom: '20px',
        }}>
          ❌ {error}
        </div>
      )}

      {/* 预测结果 */}
      {prediction && (
        <div style={{ marginTop: '40px' }}>
          <h2 style={{ fontSize: '24px', marginBottom: '20px', color: '#333', textAlign: 'center' }}>
            📊 预测结果
          </h2>

          {/* 主要预测 */}
          <div style={{
            padding: '30px',
            backgroundColor: 'white',
            borderRadius: '16px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            textAlign: 'center',
            marginBottom: '30px',
          }}>
            <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '10px', color: '#1f2937' }}>
              {prediction.predicted_score}
            </div>
            <div style={{ marginBottom: '20px' }}>
              <span style={{
                padding: '10px 30px',
                backgroundColor: '#3b82f6',
                color: 'white',
                borderRadius: '20px',
                fontSize: '18px',
                fontWeight: 'bold',
              }}>
                {prediction.predicted_winner === 'home' ? getDisplayTeamName(prediction.home_team) + ' 胜' :
                 prediction.predicted_winner === 'away' ? getDisplayTeamName(prediction.away_team) + ' 胜' :
                 '平局'}
              </span>
            </div>
            <div style={{ color: '#666', fontSize: '16px' }}>
              预测信心度：{Math.round(prediction.overall_confidence * 100)}%
            </div>
          </div>

          {/* 胜平负概率 */}
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ fontSize: '20px', marginBottom: '15px' }}>胜平负概率</h3>
            <div style={{ display: 'flex', gap: '20px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                  <span>主胜</span>
                  <span style={{ fontWeight: 'bold' }}>
                    {Math.round(prediction.home_win_probability * 100)}%
                  </span>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${prediction.home_win_probability * 100}%`,
                    backgroundColor: '#16a34a',
                  }}></div>
                </div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                  <span>平局</span>
                  <span style={{ fontWeight: 'bold' }}>
                    {Math.round(prediction.draw_probability * 100)}%
                  </span>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${prediction.draw_probability * 100}%`,
                    backgroundColor: '#9ca3af',
                  }}></div>
                </div>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                  <span>客胜</span>
                  <span style={{ fontWeight: 'bold' }}>
                    {Math.round(prediction.away_win_probability * 100)}%
                  </span>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${prediction.away_win_probability * 100}%`,
                    backgroundColor: '#dc2626',
                  }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* 九维得分 */}
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ fontSize: '20px', marginBottom: '15px' }}>九维分析得分</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              {Object.entries(prediction.dimension_scores).map(([key, value]) => (
                <div key={key} style={{ padding: '15px', backgroundColor: 'white', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                  <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                    {key === 'odds' ? '盘口赔率' :
                     key === 'injuries' ? '伤停情报' :
                     key === 'players' ? '球员状态' :
                     key === 'tactics' ? '战术相克' :
                     key === 'home_advantage' ? '主场优势' :
                     key === 'referee' ? '裁判因素' :
                     key === 'h2h' ? '历史交锋' :
                     key === 'motivation' ? '赛事战意' :
                     key === 'fitness' ? '体能状况' : key}
                  </div>
                  <div style={{ height: '6px', backgroundColor: '#e5e7eb', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{
                      height: '100%',
                      width: `${value * 100}%`,
                      backgroundColor: value > 0.6 ? '#16a34a' : value > 0.4 ? '#f59e0b' : '#ef4444',
                    }}></div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '14px', fontWeight: 'bold', marginTop: '5px' }}>
                    {Math.round(value * 100)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 推荐投注 */}
          {prediction.recommended_bet && (
            <div style={{
              padding: '20px',
              backgroundColor: '#eff6ff',
              borderRadius: '12px',
              border: '2px solid #3b82f6',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '16px', marginBottom: '10px', fontWeight: 'bold' }}>
                🎯 AI推荐投注
              </div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6' }}>
                {prediction.recommended_bet === 'home' ? '主胜' :
                 prediction.recommended_bet === 'away' ? '客胜' :
                 prediction.recommended_bet === 'draw' ? '平局' : prediction.recommended_bet}
              </div>
              <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                信心度：{Math.round((prediction.bet_confidence || 0) * 100)}%
              </div>
            </div>
          )}
        </div>
      )}

      {/* 返回首页 */}
      <div style={{ marginTop: '40px', textAlign: 'center' }}>
        <button
          onClick={() => navigate('/')}
          style={{
            padding: '12px 30px',
            backgroundColor: 'white',
            color: '#3b82f6',
            border: '2px solid #3b82f6',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
          }}
        >
          ← 返回首页
        </button>
      </div>
    </div>
  );
}
