import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { formatDate, getWinnerLabel } from '@/lib/utils';
import { CheckCircle, XCircle, TrendingUp } from 'lucide-react';

export default function HistoryPage() {
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
    fetchStats();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/predictions/history/list?limit=50');
      const data = await response.json();
      if (data.success) {
        setPredictions(data.predictions);
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/predictions/stats/accuracy');
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Prediction History</h1>
        <p className="text-muted-foreground">
          Track your past predictions and accuracy
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Predictions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total_predictions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Accuracy</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">{stats.accuracy}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Correct</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{stats.correct_predictions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Avg Confidence</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {(stats.avg_confidence * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Predictions</CardTitle>
          <CardDescription>Your prediction history with results</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : predictions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No predictions yet. Create your first prediction!
            </div>
          ) : (
            <div className="space-y-4">
              {predictions.map((prediction) => (
                <div
                  key={prediction.id}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <div className="font-medium">
                          {prediction.home_team} vs {prediction.away_team}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {prediction.league} • {formatDate(prediction.match_date)}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm">
                          Predicted: <span className="font-medium">{prediction.predicted_score}</span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {getWinnerLabel(prediction.predicted_winner)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 flex items-center gap-3">
                    {prediction.is_correct !== null && (
                      <div className="flex items-center gap-1">
                        {prediction.is_correct ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-600" />
                        )}
                      </div>
                    )}
                    <Badge variant={prediction.overall_confidence > 0.7 ? 'default' : 'secondary'}>
                      {(prediction.overall_confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
