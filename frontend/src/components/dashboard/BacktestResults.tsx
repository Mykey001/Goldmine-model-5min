import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Target, Award, AlertTriangle } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface BacktestMetrics {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  profit_factor: number;
  net_profit: number;
  gross_profit: number;
  gross_loss: number;
  avg_win: number;
  avg_loss: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  sharpe_ratio: number;
  final_equity: number;
  return_pct: number;
}

interface BacktestConfig {
  symbol: string;
  startDate: string;
  endDate: string;
  useH1Filter: boolean;
  h1EmaPeriod: number;
  minConfidence: number;
  tpPips: number;
  slPips: number;
  lotSize: number;
  startingCapital: number;
}

interface BacktestResultsProps {
  metrics: BacktestMetrics;
  config: BacktestConfig;
}

export function BacktestResults({ metrics, config }: BacktestResultsProps) {
  const isProfitable = metrics.net_profit > 0;
  const riskRewardRatio = metrics.avg_loss !== 0 ? Math.abs(metrics.avg_win / metrics.avg_loss) : 0;

  const getPerformanceColor = (value: number, threshold: number) => {
    return value >= threshold ? 'text-green-400' : 'text-red-400';
  };

  const getPerformanceBadge = () => {
    if (metrics.profit_factor >= 2 && metrics.win_rate >= 50) {
      return { label: 'Excellent', color: 'bg-green-500' };
    } else if (metrics.profit_factor >= 1.5 && metrics.win_rate >= 45) {
      return { label: 'Good', color: 'bg-blue-500' };
    } else if (metrics.profit_factor >= 1 && metrics.win_rate >= 40) {
      return { label: 'Fair', color: 'bg-yellow-500' };
    } else {
      return { label: 'Poor', color: 'bg-red-500' };
    }
  };

  const performance = getPerformanceBadge();

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="p-6 bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-slate-700">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Backtest Results</h2>
            <p className="text-slate-400">
              {config.symbol} • {config.startDate} to {config.endDate}
            </p>
          </div>
          <Badge className={`${performance.color} text-white px-4 py-2 text-lg`}>
            {performance.label}
          </Badge>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              {isProfitable ? (
                <TrendingUp className="text-green-500" size={20} />
              ) : (
                <TrendingDown className="text-red-500" size={20} />
              )}
              <span className="text-slate-400 text-sm">Net Profit</span>
            </div>
            <p className={`text-2xl font-bold ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
              ${metrics.net_profit.toFixed(2)}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              {metrics.return_pct >= 0 ? '+' : ''}{metrics.return_pct.toFixed(2)}%
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <Target className="text-blue-500" size={20} />
              <span className="text-slate-400 text-sm">Win Rate</span>
            </div>
            <p className={`text-2xl font-bold ${getPerformanceColor(metrics.win_rate, 50)}`}>
              {metrics.win_rate.toFixed(1)}%
            </p>
            <p className="text-sm text-slate-500 mt-1">
              {metrics.winning_trades}/{metrics.total_trades} wins
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <Award className="text-purple-500" size={20} />
              <span className="text-slate-400 text-sm">Profit Factor</span>
            </div>
            <p className={`text-2xl font-bold ${getPerformanceColor(metrics.profit_factor, 1.5)}`}>
              {metrics.profit_factor.toFixed(2)}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              R:R {riskRewardRatio.toFixed(2)}
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="text-yellow-500" size={20} />
              <span className="text-slate-400 text-sm">Final Equity</span>
            </div>
            <p className="text-2xl font-bold text-white">
              ${metrics.final_equity.toLocaleString()}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              from ${config.startingCapital.toLocaleString()}
            </p>
          </div>
        </div>
      </Card>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Trading Performance */}
        <Card className="p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="text-blue-500" size={20} />
            Trading Performance
          </h3>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Total Trades</span>
              <span className="text-white font-semibold">{metrics.total_trades}</span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Winning Trades</span>
              <span className="text-green-400 font-semibold">{metrics.winning_trades}</span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Losing Trades</span>
              <span className="text-red-400 font-semibold">{metrics.losing_trades}</span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Gross Profit</span>
              <span className="text-green-400 font-semibold">${metrics.gross_profit.toFixed(2)}</span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Gross Loss</span>
              <span className="text-red-400 font-semibold">${metrics.gross_loss.toFixed(2)}</span>
            </div>
            
            <div className="flex justify-between items-center py-2">
              <span className="text-slate-400">Average Win</span>
              <span className="text-green-400 font-semibold">${metrics.avg_win.toFixed(2)}</span>
            </div>
            
            <div className="flex justify-between items-center py-2">
              <span className="text-slate-400">Average Loss</span>
              <span className="text-red-400 font-semibold">${Math.abs(metrics.avg_loss).toFixed(2)}</span>
            </div>
          </div>
        </Card>

        {/* Risk Metrics */}
        <Card className="p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="text-yellow-500" size={20} />
            Risk Metrics
          </h3>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Max Drawdown</span>
              <span className="text-red-400 font-semibold">
                ${Math.abs(metrics.max_drawdown).toFixed(2)}
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Max Drawdown %</span>
              <span className="text-red-400 font-semibold">
                {Math.abs(metrics.max_drawdown_pct).toFixed(2)}%
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Sharpe Ratio</span>
              <span className={`font-semibold ${getPerformanceColor(metrics.sharpe_ratio, 1)}`}>
                {metrics.sharpe_ratio.toFixed(2)}
              </span>
            </div>
            
            <div className="flex justify-between items-center py-2 border-b border-slate-700">
              <span className="text-slate-400">Risk/Reward Ratio</span>
              <span className="text-white font-semibold">{riskRewardRatio.toFixed(2)}</span>
            </div>

            <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <h4 className="text-sm font-semibold text-slate-300 mb-3">Configuration</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">TP / SL</span>
                  <span className="text-slate-300">{config.tpPips} / {config.slPips} pips</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Lot Size</span>
                  <span className="text-slate-300">{config.lotSize}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Min Confidence</span>
                  <span className="text-slate-300">{(config.minConfidence * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">H1 Filter</span>
                  <span className="text-slate-300">
                    {config.useH1Filter ? `Yes (EMA${config.h1EmaPeriod})` : 'No'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
