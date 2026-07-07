import React, { useMemo } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { Card } from '../ui/Card';
import { TrendingUp, Activity } from 'lucide-react';

interface EquityPoint {
  timestamp: string;
  equity: number;
}

interface Trade {
  direction: string;
  entry_time: string;
  entry_price: number;
  exit_time: string;
  exit_price: number;
  profit: number;
  exit_reason: string;
  confidence: number;
}

interface BacktestChartProps {
  equityCurve: EquityPoint[];
  trades: Trade[];
  startingCapital: number;
}

export function BacktestChart({ equityCurve, trades, startingCapital }: BacktestChartProps) {
  // Prepare equity curve data
  const equityData = useMemo(() => {
    return equityCurve.map((point, index) => ({
      index,
      equity: point.equity,
      timestamp: new Date(point.timestamp).toLocaleDateString(),
      profit: point.equity - startingCapital,
    }));
  }, [equityCurve, startingCapital]);

  // Prepare trade distribution data
  const tradeDistribution = useMemo(() => {
    const bins: { [key: string]: number } = {};
    const binSize = 50; // $50 bins

    trades.forEach((trade) => {
      const profit = Math.round(trade.profit / binSize) * binSize;
      const key = `${profit}`;
      bins[key] = (bins[key] || 0) + 1;
    });

    return Object.entries(bins)
      .map(([profit, count]) => ({
        profit: parseInt(profit),
        count,
      }))
      .sort((a, b) => a.profit - b.profit);
  }, [trades]);

  // Calculate drawdown data
  const drawdownData = useMemo(() => {
    let maxEquity = startingCapital;
    return equityData.map((point) => {
      maxEquity = Math.max(maxEquity, point.equity);
      const drawdown = point.equity - maxEquity;
      const drawdownPct = (drawdown / maxEquity) * 100;
      
      return {
        index: point.index,
        timestamp: point.timestamp,
        drawdown,
        drawdownPct,
      };
    });
  }, [equityData, startingCapital]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
          <p className="text-slate-300 text-sm mb-1">{payload[0].payload.timestamp}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: ${entry.value.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Equity Curve */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="text-green-500" size={24} />
          <h3 className="text-xl font-bold text-white">Equity Curve</h3>
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={equityData}>
            <defs>
              <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              dataKey="index" 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
              label={{ value: 'Trade Number', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
            />
            <YAxis 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
              label={{ value: 'Equity ($)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={startingCapital} stroke="#ef4444" strokeDasharray="3 3" label="Start" />
            <Area
              type="monotone"
              dataKey="equity"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#equityGradient)"
              name="Equity"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Drawdown Chart */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="text-red-500" size={24} />
          <h3 className="text-xl font-bold text-white">Drawdown</h3>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={drawdownData}>
            <defs>
              <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              dataKey="index" 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
              label={{ value: 'Trade Number', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
            />
            <YAxis 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
              label={{ value: 'Drawdown ($)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#64748b" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="drawdown"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#drawdownGradient)"
              name="Drawdown"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Trade Distribution */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="text-purple-500" size={24} />
          <h3 className="text-xl font-bold text-white">Profit/Loss Distribution</h3>
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={tradeDistribution}>
            <defs>
              <linearGradient id="distributionGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              dataKey="profit" 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
              label={{ value: 'Profit/Loss ($)', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
            />
            <YAxis 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8' }}
              label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip 
              content={({ active, payload }: any) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg">
                      <p className="text-slate-300 text-sm">
                        Profit: ${payload[0].payload.profit}
                      </p>
                      <p className="text-purple-400 text-sm">
                        Count: {payload[0].payload.count}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine x={0} stroke="#ef4444" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#8b5cf6"
              strokeWidth={2}
              fill="url(#distributionGradient)"
              name="Frequency"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Trade List */}
      <Card className="p-6">
        <h3 className="text-xl font-bold text-white mb-4">Recent Trades</h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Direction</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Entry</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Exit</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Profit</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Reason</th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {trades.slice(-20).reverse().map((trade, index) => (
                <tr key={index} className="border-b border-slate-800 hover:bg-slate-800/50">
                  <td className="py-3 px-4">
                    <span className={`font-semibold ${trade.direction === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                      {trade.direction}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300 text-sm">
                    {new Date(trade.entry_time).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-slate-300 text-sm">
                    {new Date(trade.exit_time).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`font-semibold ${trade.profit > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${trade.profit.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`text-xs px-2 py-1 rounded ${
                      trade.exit_reason === 'TP' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
                    }`}>
                      {trade.exit_reason}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-300">
                    {(trade.confidence * 100).toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
