import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { Card } from '../ui/Card';
import { useMetricsStore } from '../../store/metricsStore';
import { formatCurrency, formatDateTime } from '../../utils/formatters';

export const EquityCurve: React.FC = () => {
  const equityCurve = useMetricsStore((state) => state.equityCurve);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 shadow-xl">
          <p className="text-slate-300 text-xs mb-1">
            {formatDateTime(payload[0].payload.timestamp)}
          </p>
          <p className="text-green-400 font-semibold">
            Equity: {formatCurrency(payload[0].value)}
          </p>
          {payload[1] && (
            <p className="text-blue-400 font-semibold">
              Balance: {formatCurrency(payload[1].value)}
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <Card title="Equity Curve">
      {equityCurve.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-slate-400">
          No equity data available yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={equityCurve}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="timestamp"
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: '10px' }}
              iconType="line"
              formatter={(value) => (
                <span className="text-slate-300 text-sm">{value}</span>
              )}
            />
            <Line
              type="monotone"
              dataKey="equity"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Equity"
            />
            <Line
              type="monotone"
              dataKey="balance"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="Balance"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  );
};
