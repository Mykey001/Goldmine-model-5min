import React from 'react';
import { Activity, ArrowUpCircle, ArrowDownCircle, MinusCircle } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useTradesStore } from '../../store/tradesStore';
import { formatTime, formatPrice } from '../../utils/formatters';

export const SignalHistory: React.FC = () => {
  const signals = useTradesStore((state) => state.signals);

  const getSignalIcon = (direction: string) => {
    switch (direction) {
      case 'BUY':
        return <ArrowUpCircle className="text-green-400" size={20} />;
      case 'SELL':
        return <ArrowDownCircle className="text-red-400" size={20} />;
      default:
        return <MinusCircle className="text-slate-400" size={20} />;
    }
  };

  const getSignalColor = (direction: string) => {
    switch (direction) {
      case 'BUY':
        return 'border-l-green-500';
      case 'SELL':
        return 'border-l-red-500';
      default:
        return 'border-l-slate-500';
    }
  };

  return (
    <Card title="Signal History" className="h-full">
      {signals.length === 0 ? (
        <div className="text-center py-8 text-slate-400">
          <Activity className="mx-auto mb-2 opacity-50" size={48} />
          <p>No signals generated yet</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {signals.slice(0, 20).map((signal) => (
            <div
              key={signal.id}
              className={`bg-slate-700/50 rounded-lg p-3 border-l-4 ${getSignalColor(
                signal.direction
              )} hover:bg-slate-700 transition-colors`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getSignalIcon(signal.direction)}
                  <span className="font-semibold text-white">{signal.symbol}</span>
                  <Badge
                    variant={
                      signal.direction === 'BUY'
                        ? 'success'
                        : signal.direction === 'SELL'
                        ? 'danger'
                        : 'default'
                    }
                  >
                    {signal.direction}
                  </Badge>
                </div>
                <span className="text-xs text-slate-400">
                  {formatTime(signal.timestamp)}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-slate-400">Price:</span>
                  <span className="text-white ml-2 font-mono">
                    {formatPrice(signal.entry_price || 0, 2)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Confidence:</span>
                  <span
                    className={`ml-2 font-semibold ${
                      signal.confidence >= 0.7
                        ? 'text-green-400'
                        : signal.confidence >= 0.5
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`}
                  >
                    {((signal.confidence || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {signal.executed && (
                <div className="mt-2">
                  <Badge variant="success">Executed</Badge>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
