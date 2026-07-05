import React from 'react';
import { History } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useTradesStore } from '../../store/tradesStore';
import {
  formatCurrency,
  formatDateTime,
  formatDuration,
  getProfitBgColor,
} from '../../utils/formatters';

export const TradeHistory: React.FC = () => {
  const closedTrades = useTradesStore((state) => state.closedTrades);

  return (
    <Card title="Trade History">
      {closedTrades.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          <History className="mx-auto mb-2 opacity-50" size={48} />
          <p>No closed trades yet</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-medium">
                  Time
                </th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">
                  Symbol
                </th>
                <th className="text-left py-3 px-4 text-slate-400 font-medium">
                  Direction
                </th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">
                  Entry
                </th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">
                  Exit
                </th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">
                  Duration
                </th>
                <th className="text-right py-3 px-4 text-slate-400 font-medium">
                  Profit
                </th>
              </tr>
            </thead>
            <tbody>
              {closedTrades.slice(0, 10).map((trade) => (
                <tr
                  key={trade.id}
                  className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="py-3 px-4 text-slate-300">
                    {formatDateTime(trade.exit_time)}
                  </td>
                  <td className="py-3 px-4 text-white font-medium">
                    {trade.symbol}
                  </td>
                  <td className="py-3 px-4">
                    <Badge
                      variant={trade.direction === 'BUY' ? 'success' : 'danger'}
                    >
                      {trade.direction}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300 font-mono">
                    {trade.entry_price.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300 font-mono">
                    {trade.exit_price.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-400">
                    {formatDuration(trade.duration_minutes)}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <span
                      className={`font-semibold px-2 py-1 rounded ${getProfitBgColor(
                        trade.profit
                      )}`}
                    >
                      {formatCurrency(trade.profit)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
};
