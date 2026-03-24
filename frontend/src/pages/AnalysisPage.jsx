import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { getDimensionLabel, formatPercentage } from '@/lib/utils.js';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

export default function AnalysisPage() {
  const { matchId } = useParams();
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    fetchAnalysis();
  }, [matchId]);

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`/api/analysis/nine-dimensions/${matchId}`);
      const data = await response.json();
      if (data.success) {
        setAnalysis(data);
      }
    } catch (error) {
      console.error('Error fetching analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading analysis...</div>;
  }

  if (!analysis) {
    return <div className="text-center py-12">Analysis not found</div>;
  }

  // Prepare radar chart data
  const radarData = Object.entries(analysis.dimension_scores).map(([key, value]) => ({
    dimension: getDimensionLabel(key),
    value: value * 100,
    fullMark: 100,
  }));

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Nine-Dimensional Analysis</h1>
        <p className="text-muted-foreground">
          {analysis.home_team} vs {analysis.away_team}
        </p>
      </div>

      {/* Radar chart */}
      <Card>
        <CardHeader>
          <CardTitle>Dimension Scores</CardTitle>
          <CardDescription>
            Visual breakdown of all nine dimensions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Score"
                  dataKey="value"
                  stroke="hsl(var(--primary))"
                  fill="hsl(var(--primary))"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Detailed scores */}
      <div className="grid md:grid-cols-2 gap-6">
        {Object.entries(analysis.dimension_scores).map(([key, value]) => (
          <Card key={key}>
            <CardHeader>
              <CardTitle className="text-lg">{getDimensionLabel(key)}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Progress value={value * 100} />
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">
                    {value < 0.4 ? 'Favors Away' : value > 0.6 ? 'Favors Home' : 'Neutral'}
                  </span>
                  <span className="font-medium">{formatPercentage(value)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Summary</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span>Predicted Winner:</span>
            <Badge variant="default" className="text-lg px-4 py-1">
              {analysis.predicted_winner === 'home' ? analysis.home_team + ' Wins' :
               analysis.predicted_winner === 'away' ? analysis.away_team + ' Wins' :
               'Draw'}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span>Overall Confidence:</span>
            <span className="font-medium">{formatPercentage(analysis.confidence)}</span>
          </div>

          {analysis.insights && analysis.insights.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold">Key Insights</h3>
              <ul className="space-y-1">
                {analysis.insights.map((insight, i) => (
                  <li key={i} className="text-sm text-muted-foreground">• {insight}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.risks && analysis.risks.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold text-destructive">Risk Factors</h3>
              <ul className="space-y-1">
                {analysis.risks.map((risk, i) => (
                  <li key={i} className="text-sm text-muted-foreground">⚠ {risk}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
