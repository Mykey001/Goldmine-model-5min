import React, { useState, useEffect } from 'react';
import { Settings, Save, AlertTriangle } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import * as api from '../../services/api';

export const SettingsPanel: React.FC = () => {
  const [config, setConfig] = useState({
    max_daily_loss: 400,
    max_positions: 1,
    min_confidence: 0.5,
    default_lot_size: 0.01,
    tp_pips: 100,
    sl_pips: 50,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setIsLoading(true);
    try {
      const currentConfig = await api.getConfig();
      setConfig(currentConfig);
    } catch (err: any) {
      setError('Failed to load configuration');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await api.updateConfig(config);
      setSuccess('Configuration updated successfully!');
    } catch (err: any) {
      setError(err.message || 'Failed to update configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (key: string, value: number) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <Card title="Risk Management Settings" className="mb-6">
      <div className="space-y-6">
        {/* Warning */}
        <div className="p-3 bg-yellow-900/20 border border-yellow-700 rounded-lg flex items-start gap-2">
          <AlertTriangle size={20} className="text-yellow-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-yellow-200">
            Changes take effect immediately. Always test on demo account first!
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="p-3 bg-green-900/30 border border-green-700 rounded-lg text-green-300 text-sm">
            {success}
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-8 text-slate-400">Loading configuration...</div>
        ) : (
          <div className="space-y-4">
            {/* Max Daily Loss */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Daily Loss ($)
              </label>
              <input
                type="number"
                value={config.max_daily_loss}
                onChange={(e) => handleChange('max_daily_loss', parseFloat(e.target.value))}
                step="10"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="text-xs text-slate-400 mt-1">
                Trading stops when daily loss reaches this amount
              </div>
            </div>

            {/* Max Positions */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Max Simultaneous Positions
              </label>
              <input
                type="number"
                value={config.max_positions}
                onChange={(e) => handleChange('max_positions', parseInt(e.target.value))}
                min="1"
                max="10"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="text-xs text-slate-400 mt-1">
                Maximum number of open positions at once
              </div>
            </div>

            {/* Min Confidence */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Min Confidence Threshold ({(config.min_confidence * 100).toFixed(0)}%)
              </label>
              <input
                type="range"
                value={config.min_confidence}
                onChange={(e) => handleChange('min_confidence', parseFloat(e.target.value))}
                min="0.3"
                max="0.9"
                step="0.05"
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>30% (Aggressive)</span>
                <span>50% (Balanced)</span>
                <span>90% (Conservative)</span>
              </div>
              <div className="text-xs text-slate-400 mt-2">
                Only trade when ML model confidence is above this level
              </div>
            </div>

            {/* Default Lot Size */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Default Lot Size
              </label>
              <input
                type="number"
                value={config.default_lot_size}
                onChange={(e) => handleChange('default_lot_size', parseFloat(e.target.value))}
                min="0.01"
                max="10"
                step="0.01"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="text-xs text-slate-400 mt-1">
                Volume for each trade (0.01 = 0.01 lots)
              </div>
            </div>

            {/* Take Profit Pips */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Take Profit (Pips)
              </label>
              <input
                type="number"
                value={config.tp_pips}
                onChange={(e) => handleChange('tp_pips', parseFloat(e.target.value))}
                min="10"
                max="500"
                step="10"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="text-xs text-slate-400 mt-1">
                Profit target distance from entry
              </div>
            </div>

            {/* Stop Loss Pips */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Stop Loss (Pips)
              </label>
              <input
                type="number"
                value={config.sl_pips}
                onChange={(e) => handleChange('sl_pips', parseFloat(e.target.value))}
                min="10"
                max="300"
                step="10"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="text-xs text-slate-400 mt-1">
                Maximum loss distance from entry
              </div>
            </div>

            {/* Risk/Reward Ratio */}
            <div className="p-4 bg-slate-700/50 rounded-lg">
              <div className="text-sm text-slate-300 mb-1">Risk/Reward Ratio</div>
              <div className="text-2xl font-bold text-white">
                1:{(config.tp_pips / config.sl_pips).toFixed(2)}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                {config.tp_pips / config.sl_pips >= 2
                  ? '✓ Good - Target is 2x+ risk'
                  : config.tp_pips / config.sl_pips >= 1.5
                  ? '⚠ Acceptable - Target is 1.5x+ risk'
                  : '⚠ Risky - Target should be at least 1.5x risk'}
              </div>
            </div>

            {/* Save Button */}
            <Button
              onClick={handleSave}
              variant="success"
              className="w-full"
              isLoading={isSaving}
            >
              <Save size={16} className="mr-2" />
              Save Configuration
            </Button>

            {/* Presets */}
            <div>
              <div className="text-sm font-medium text-slate-300 mb-2">Quick Presets:</div>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() =>
                    setConfig({
                      max_daily_loss: 200,
                      max_positions: 1,
                      min_confidence: 0.7,
                      default_lot_size: 0.01,
                      tp_pips: 50,
                      sl_pips: 25,
                    })
                  }
                >
                  Conservative
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() =>
                    setConfig({
                      max_daily_loss: 400,
                      max_positions: 1,
                      min_confidence: 0.5,
                      default_lot_size: 0.01,
                      tp_pips: 100,
                      sl_pips: 50,
                    })
                  }
                >
                  Balanced
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() =>
                    setConfig({
                      max_daily_loss: 1000,
                      max_positions: 3,
                      min_confidence: 0.3,
                      default_lot_size: 0.05,
                      tp_pips: 200,
                      sl_pips: 100,
                    })
                  }
                >
                  Aggressive
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
