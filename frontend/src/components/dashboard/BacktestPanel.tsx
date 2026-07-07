import React, { useState } from 'react';
import { Play, Settings, TrendingUp, TrendingDown, DollarSign, Target, AlertCircle } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { BacktestResults } from './BacktestResults';
import { BacktestChart } from './BacktestChart';

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
  useVolatilityFilter: boolean;
  minAtr: number;
  maxAtr: number;
}

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

interface BacktestResult {
  success: boolean;
  metrics: BacktestMetrics;
  trades: any[];
  equity_curve: any[];
  config: BacktestConfig;
  symbol: string;
  start_date: string;
  end_date: string;
  total_candles: number;
}

export function BacktestPanel() {
  const [config, setConfig] = useState<BacktestConfig>({
    symbol: 'XAUUSDm',
    startDate: '2025-05-01',
    endDate: '2025-07-03',
    useH1Filter: true,
    h1EmaPeriod: 200,
    minConfidence: 0.5,
    tpPips: 100,
    slPips: 50,
    lotSize: 0.01,
    startingCapital: 10000,
    useVolatilityFilter: false,
    minAtr: 0.5,
    maxAtr: 5.0,
  });

  const [results, setResults] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const runBacktest = async () => {
    setLoading(true);
    setError(null);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Build query parameters
      const params = new URLSearchParams({
        symbol: config.symbol,
        start_date: new Date(config.startDate).toISOString(),
        end_date: new Date(config.endDate).toISOString(),
        use_h1_filter: config.useH1Filter.toString(),
        h1_ema_period: config.h1EmaPeriod.toString(),
        min_confidence: config.minConfidence.toString(),
        tp_pips: config.tpPips.toString(),
        sl_pips: config.slPips.toString(),
        lot_size: config.lotSize.toString(),
        starting_capital: config.startingCapital.toString(),
        use_volatility_filter: config.useVolatilityFilter.toString(),
        min_atr: config.minAtr.toString(),
        max_atr: config.maxAtr.toString(),
      });

      const response = await fetch(`${apiUrl}/api/backtest/run?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Backtest failed');
      }

      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      let errorMessage = err.message || 'Failed to run backtest';
      
      // Provide helpful error messages
      if (errorMessage.includes('No data returned') || errorMessage.includes('Failed to fetch')) {
        errorMessage = 'Failed to fetch data from MT5. Please ensure:\n' +
                      '1. MT5 is running and connected\n' +
                      '2. You are connected to a terminal (use Live Trading tab first)\n' +
                      '3. The symbol exists and has historical data\n' +
                      '4. The date range is valid for your broker';
      } else if (errorMessage.includes('Model not loaded')) {
        errorMessage = 'ML model not loaded. Please ensure the model file exists at:\n' +
                      'models/final/xgboost_model.pkl';
      } else if (errorMessage.includes('feature')) {
        errorMessage = 'Feature mismatch error. The model may need retraining.\n' +
                      'Original error: ' + errorMessage;
      }
      
      setError(errorMessage);
      console.error('Backtest error:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = (key: keyof BacktestConfig, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const exportToCSV = async () => {
    if (!results) return;
    
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/backtest/export/csv`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(results),
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`✅ Exported ${data.trades_count} trades to ${data.filename}\n\nFile location: ${data.filepath}`);
      } else {
        alert(`❌ Export failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err: any) {
      console.error('Export error:', err);
      alert(`❌ Export failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Panel */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Settings className="text-blue-500" size={24} />
            <h2 className="text-2xl font-bold text-white">Backtest Configuration</h2>
          </div>
          <Button
            onClick={runBacktest}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600"
          >
            {loading ? (
              <>
                <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                Running...
              </>
            ) : (
              <>
                <Play size={16} className="mr-2" />
                Run Backtest
              </>
            )}
          </Button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-900/20 border border-red-500 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <p className="text-red-400 font-semibold">Error</p>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Basic Configuration */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Symbol</label>
            <input
              type="text"
              value={config.symbol}
              onChange={(e) => updateConfig('symbol', e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Start Date</label>
            <input
              type="date"
              value={config.startDate}
              onChange={(e) => updateConfig('startDate', e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">End Date</label>
            <input
              type="date"
              value={config.endDate}
              onChange={(e) => updateConfig('endDate', e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Risk Management */}
        <div className="border-t border-slate-700 pt-4 mb-4">
          <h3 className="text-lg font-semibold text-white mb-3">Risk Management</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Take Profit (pips)</label>
              <input
                type="number"
                value={config.tpPips}
                onChange={(e) => updateConfig('tpPips', parseInt(e.target.value))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Stop Loss (pips)</label>
              <input
                type="number"
                value={config.slPips}
                onChange={(e) => updateConfig('slPips', parseInt(e.target.value))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Lot Size</label>
              <input
                type="number"
                step="0.01"
                value={config.lotSize}
                onChange={(e) => updateConfig('lotSize', parseFloat(e.target.value))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Starting Capital ($)</label>
              <input
                type="number"
                value={config.startingCapital}
                onChange={(e) => updateConfig('startingCapital', parseInt(e.target.value))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Advanced Settings */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-400 hover:text-blue-300 text-sm font-medium mb-3"
        >
          {showAdvanced ? '▼' : '▶'} Advanced Settings
        </button>

        {showAdvanced && (
          <div className="border-t border-slate-700 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Min Confidence</label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="1"
                  value={config.minConfidence}
                  onChange={(e) => updateConfig('minConfidence', parseFloat(e.target.value))}
                  className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center gap-3 pt-6">
                <input
                  type="checkbox"
                  id="h1Filter"
                  checked={config.useH1Filter}
                  onChange={(e) => updateConfig('useH1Filter', e.target.checked)}
                  className="w-5 h-5 rounded border-slate-600 bg-slate-700 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="h1Filter" className="text-sm font-medium text-slate-300">
                  Use H1 Trend Filter
                </label>
              </div>

              {config.useH1Filter && (
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">H1 EMA Period</label>
                  <input
                    type="number"
                    value={config.h1EmaPeriod}
                    onChange={(e) => updateConfig('h1EmaPeriod', parseInt(e.target.value))}
                    className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}
            </div>

            {/* Volatility Filter */}
            <div className="border-t border-slate-700 pt-4 mt-4">
              <div className="flex items-center gap-3 mb-3">
                <input
                  type="checkbox"
                  id="volFilter"
                  checked={config.useVolatilityFilter}
                  onChange={(e) => updateConfig('useVolatilityFilter', e.target.checked)}
                  className="w-5 h-5 rounded border-slate-600 bg-slate-700 text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <label htmlFor="volFilter" className="text-sm font-medium text-slate-300">
                  Use Volatility Filter (ATR)
                </label>
              </div>

              {config.useVolatilityFilter && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Min ATR</label>
                    <input
                      type="number"
                      step="0.1"
                      value={config.minAtr}
                      onChange={(e) => updateConfig('minAtr', parseFloat(e.target.value))}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Max ATR</label>
                    <input
                      type="number"
                      step="0.1"
                      value={config.maxAtr}
                      onChange={(e) => updateConfig('maxAtr', parseFloat(e.target.value))}
                      className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Results Display */}
      {results && !loading && (
        <>
          <div className="flex justify-end mb-4">
            <Button
              onClick={exportToCSV}
              className="bg-green-600 hover:bg-green-700"
            >
              📊 Export to CSV
            </Button>
          </div>
          <BacktestResults metrics={results.metrics} config={config} />
          <BacktestChart 
            equityCurve={results.equity_curve} 
            trades={results.trades}
            startingCapital={config.startingCapital}
          />
        </>
      )}
    </div>
  );
}
