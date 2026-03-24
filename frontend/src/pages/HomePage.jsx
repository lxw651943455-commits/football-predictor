import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    try {
      // 从后端获取今日比赛（包含赔率）
      const response = await fetch('http://127.0.0.1:5000/api/matches/today');
      const data = await response.json();
      if (data.success && data.matches) {
        setMatches(data.matches);
      }
    } catch (error) {
      console.error('获取比赛失败:', error);
      // 使用默认比赛数据
      setMatches([
        {
          id: '1',
          home_team: '阿森纳',
          away_team: '切尔西',
          league: '英超',
          match_date: new Date().toISOString(),
          home_odds: 2.10,
          draw_odds: 3.40,
          away_odds: 3.60,
        },
        {
          id: '2',
          home_team: '曼城',
          away_team: '利物浦',
          league: '英超',
          match_date: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
          home_odds: 1.85,
          draw_odds: 3.60,
          away_odds: 4.20,
        },
        {
          id: '3',
          home_team: '皇家马德里',
          away_team: '巴塞罗那',
          league: '西甲',
          match_date: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(),
          home_odds: 2.50,
          draw_odds: 3.20,
          away_odds: 2.80,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = (match) => {
    // 跳转到预测页面，并传递比赛信息
    const params = new URLSearchParams({
      home: match.home_team,
      away: match.away_team,
      league: match.league,
      homeOdds: match.home_odds,
      drawOdds: match.draw_odds,
      awayOdds: match.away_odds,
    });
    navigate(`/predict?${params.toString()}`);
  };

  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Hero section */}
      <div style={{ textAlign: 'center', marginBottom: '60px' }}>
        <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '20px' }}>
          ⚽ 足球比分预测 - 九维全息分析
        </h1>
        <p style={{ fontSize: '20px', color: '#666', marginBottom: '40px' }}>
          基于九维全息赛事演算模型的专业足球比分预测系统
        </p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
          <button
            onClick={() => navigate('/predict')}
            style={{
              padding: '15px 40px',
              fontSize: '18px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            🔮 自定义预测
          </button>
          <button
            onClick={() => navigate('/history')}
            style={{
              padding: '15px 40px',
              fontSize: '18px',
              backgroundColor: 'white',
              color: '#3b82f6',
              border: '2px solid #3b82f6',
              borderRadius: '8px',
              cursor: 'pointer',
            }}
          >
            📊 历史记录
          </button>
        </div>
      </div>

      {/* Today's Matches */}
      <div style={{ marginBottom: '60px' }}>
        <h2 style={{ fontSize: '32px', marginBottom: '30px', textAlign: 'center' }}>
          📅 今日热门比赛（含实时赔率）
        </h2>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            加载中...
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '20px' }}>
            {matches.map((match) => (
              <div
                key={match.id}
                style={{
                  padding: '25px',
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  border: '2px solid #e5e7eb',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = '#3b82f6'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = '#e5e7eb'}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
                    {match.home_team} vs {match.away_team}
                  </div>
                  <div style={{ color: '#666', marginBottom: '12px' }}>
                    🏆 {match.league}
                  </div>
                  <div style={{ display: 'flex', gap: '20px', fontSize: '14px' }}>
                    <div>
                      <span style={{ color: '#999' }}>主胜赔率：</span>
                      <span style={{ fontWeight: 'bold', color: '#16a34a' }}>{match.home_odds}</span>
                    </div>
                    <div>
                      <span style={{ color: '#999' }}>平局：</span>
                      <span style={{ fontWeight: 'bold' }}>{match.draw_odds}</span>
                    </div>
                    <div>
                      <span style={{ color: '#999' }}>客胜：</span>
                      <span style={{ fontWeight: 'bold', color: '#dc2626' }}>{match.away_odds}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handlePredict(match)}
                  style={{
                    padding: '12px 30px',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    marginLeft: '20px',
                  }}
                >
                  🔮 预测
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Features */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', marginBottom: '60px' }}>
        <div style={{ padding: '30px', border: '1px solid #e5e7eb', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '20px', marginBottom: '15px' }}>🎯 九维分析模型</h3>
          <p style={{ color: '#666', lineHeight: '1.6' }}>
            盘口赔率、伤停情报、球员状态、战术相克、主场优势、裁判因素、历史交锋、赛事战意、体能状况
          </p>
        </div>

        <div style={{ padding: '30px', border: '1px solid #e5e7eb', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '20px', marginBottom: '15px' }}>📈 实时赔率数据</h3>
          <p style={{ color: '#666', lineHeight: '1.6' }}>
            集成The Odds API，自动获取最新赔率，支持多个博彩公司的赔率对比分析
          </p>
        </div>

        <div style={{ padding: '30px', border: '1px solid #e5e7eb', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '20px', marginBottom: '15px' }}>📊 准确率追踪</h3>
          <p style={{ color: '#666', lineHeight: '1.6' }}>
            记录预测历史，追踪准确率，生成深度分析报告
          </p>
        </div>
      </div>
    </div>
  );
}
