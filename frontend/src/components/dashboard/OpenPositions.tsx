import React from 'react';
import { X, TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { useTradesStore } from '../../store/tradesStore';
import {
  formatCurrency,
  formatPrice,
  formatRelativeTime,
  getProfitColor,
  getDirectionColor,
} from '../../utils/formatters';
import { closePosition } from '../../services/api';

export const OpenPositions: React.FC = () => {
  const positions = useTradesStore((state) => state.openPositions);
  const [closingTicket, setClosingTicket] = React.useState<number | null>(null);

  const handleClosePosition = async (ticket: number) => {
    setClosingTicket(ticket);
    try {
      await closePosition(ticket);
    } catch (error) {
      console.error('Failed to close position:', error);
    } finally {
      setClosingTicket(null);
    }
  };

  return (
    <Card title="Open Positions" className="h-full">
      {positions.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          <TrendingUp className="mx-auto mb-2 opacity-50" size={48} />
          <p>No open positions</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto">
          {positions.map((position) => (
            <div
              key={position.ticket}
              className="bg-slate-700/50 rounded-lg p-4 hover:bg-slate-700 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white text-lg">
                    {position.symbol ?? 'N/A'}
                  </span>
                  <Badge
                    variant={position.direction === 'BUY' ? 'success' : 'danger'}
                  >
                    {position.direction ?? 'N/A'}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xl font-bold ${getProfitColor(position.profit ?? 0)}`}>
                    {formatCurrency(position.profit ?? 0)}
                  </span>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleClosePosition(position.ticket)}
                    isLoading={closingTicket === position.ticket}
                    className="p-1"
                  >
                    <X size={16} />
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-slate-400">Entry:</span>
                  <span className="text-white ml-2 font-mono">
                    {formatPrice(position.entry_price ?? 0, 2)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Current:</span>
                  <span className="text-white ml-2 font-mono">
                    {formatPrice(position.current_price ?? 0, 2)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">TP:</span>
                  <span className="text-green-400 ml-2 font-mono">
                    {formatPrice(position.tp ?? 0, 2)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">SL:</span>
                  <span className="text-red-400 ml-2 font-mono">
                    {formatPrice(position.sl ?? 0, 2)}
                  </span>
                </div>
              </div>

              <div className="mt-2 text-xs text-slate-400 flex justify-between items-center">
                <span>Vol: {position.volume ?? 0}</span>
                <span>Opened {position.open_time ? formatRelativeTime(position.open_time) : 'N/A'}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
