import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Target, Trophy, AlertTriangle } from 'lucide-react';
import { MetricCard } from '../ui/Card';
import { useAccountStore } from '../../store/accountStore';
import { useMetricsStore } from '../../store/metricsStore';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

export const MetricsOverview: React.FC = () => {
  const account = useAccountStore((state) => state.account);
  const summary = useMetricsStore((state) => state.summary);
  const daily = useMetricsStore((state) => state.daily);

  const dailyPnlPct = account
    ? ((daily?.net_profit || 0) / account.balance) * 100
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        label="Account Balance"
        value={formatCurrency(account?.balance || 0)}
        icon={<DollarSign size={24} />}
      />

      <MetricCard
        label="Today's P&L"
        value={formatCurrency(daily?.net_profit || 0)}
        change={dailyPnlPct}
        icon={
          dailyPnlPct >= 0 ? (
            <TrendingUp size={24} className="text-green-400" />
          ) : (
            <TrendingDown size={24} className="text-red-400" />
          )
        }
      />

      <MetricCard
        label="Win Rate"
        value={formatPercentage(summary?.win_rate || 0, 1)}
        icon={<Target size={24} />}
      />

      <MetricCard
        label="Profit Factor"
        value={(summary?.profit_factor || 0).toFixed(2)}
        icon={<Trophy size={24} />}
      />
    </div>
  );
};
