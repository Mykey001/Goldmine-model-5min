import React, { useState, useEffect } from 'react';
import { Settings, Wifi, Terminal, TrendingUp, RefreshCw } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import * as api from '../../services/api';
import { useConnectionStore } from '../../store/connectionStore';
import type { Terminal as TerminalType } from '../../types';

export const ConnectionPanel: React.FC = () => {
  const [terminals, setTerminals] = useState<TerminalType[]>([]);
  const [selectedTerminal, setSelectedTerminal] = useState<string>('');
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [server, setServer] = useState('');
  const [symbol, setSymbol] = useState('XAUUSDm');
  const [isLoading, setIsLoading] = useState(false);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const { isConnected, setConnected, setActiveTerminal, setCurrentSymbol } = useConnectionStore();

  const discoverTerminals = async () => {
    setIsDiscovering(true);
    setError(null);
    try {
      const discoveredTerminals = await api.discoverTerminals();
      setTerminals(discoveredTerminals || []);
      if (discoveredTerminals && discoveredTerminals.length > 0) {
        setSelectedTerminal(discoveredTerminals[0].id);
        setSuccess(`Found ${discoveredTerminals.length} MT5 terminal(s)`);
      } else {
        setError('No MT5 terminals found. Please install MetaTrader 5.');
      }
    } catch (err: any) {
      setTerminals([]);
      setError(err.message || 'Failed to discover terminals');
    } finally {
      setIsDiscovering(false);
    }
  };

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await api.connectTerminal({
        terminal_id: selectedTerminal,
        account: parseInt(account),
        password,
        server,
      });

      if (result.success) {
        setConnected(true);
        setActiveTerminal(result.terminal);
        setSuccess('Connected to MT5 successfully!');
        
        // Auto-select symbol after connection
        if (symbol) {
          await handleSelectSymbol();
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to MT5');
      setConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectSymbol = async () => {
    try {
      await api.selectSymbol(symbol);
      setCurrentSymbol(symbol);
      setSuccess(`Symbol changed to ${symbol}`);
    } catch (err: any) {
      setError(err.message || 'Failed to select symbol');
    }
  };

  useEffect(() => {
    // Auto-discover terminals on mount
    discoverTerminals();
  }, []);

  return (
    <Card title="Connection & Settings" className="mb-6">
      <div className="space-y-6">
        {/* Status Indicator */}
        <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
          <div className="flex items-center gap-3">
            <Wifi
              size={24}
              className={isConnected ? 'text-green-400' : 'text-red-400'}
            />
            <div>
              <div className="font-semibold text-white">
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              <div className="text-sm text-slate-400">
                {isConnected ? 'MT5 connection active' : 'Not connected to MT5'}
              </div>
            </div>
          </div>
          <Badge variant={isConnected ? 'success' : 'danger'}>
            {isConnected ? 'Active' : 'Inactive'}
          </Badge>
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

        {!isConnected ? (
          <>
            {/* Terminal Discovery */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-slate-300">
                  <Terminal className="inline mr-2" size={16} />
                  MT5 Terminal
                </label>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={discoverTerminals}
                  isLoading={isDiscovering}
                >
                  <RefreshCw size={14} className="mr-1" />
                  Discover
                </Button>
              </div>
              
              {terminals.length > 0 ? (
                <select
                  value={selectedTerminal}
                  onChange={(e) => setSelectedTerminal(e.target.value)}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {terminals.map((terminal) => (
                    <option key={terminal.id} value={terminal.id}>
                      {terminal.name} - {terminal.path}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="text-sm text-slate-400 text-center py-4 border border-slate-700 rounded-lg">
                  No terminals found. Click "Discover" to search.
                </div>
              )}
            </div>

            {/* Connection Form */}
            <form onSubmit={handleConnect} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Account Number
                </label>
                <input
                  type="number"
                  value={account}
                  onChange={(e) => setAccount(e.target.value)}
                  placeholder="12345678"
                  required
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Server
                </label>
                <input
                  type="text"
                  value={server}
                  onChange={(e) => setServer(e.target.value)}
                  placeholder="YourBroker-Demo"
                  required
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  <TrendingUp className="inline mr-2" size={16} />
                  Trading Symbol
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="XAUUSDm"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="text-xs text-slate-400 mt-1">
                  Enter any symbol available in your MT5 (e.g., XAUUSDm, EURUSD, BTCUSD)
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                className="w-full"
                isLoading={isLoading}
                disabled={!selectedTerminal || !account || !password || !server}
              >
                Connect to MT5
              </Button>
            </form>
          </>
        ) : (
          <div className="space-y-4">
            <div className="p-4 bg-green-900/20 border border-green-700 rounded-lg">
              <div className="font-semibold text-green-300 mb-2">
                ✓ Connected Successfully
              </div>
              <div className="text-sm text-slate-300">
                The system is now monitoring M5 bars and will execute trades automatically
                based on ML signals.
              </div>
            </div>

            {/* Symbol Selector (when connected) */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                <TrendingUp className="inline mr-2" size={16} />
                Change Trading Symbol
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="XAUUSDm"
                  className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Button onClick={handleSelectSymbol} variant="primary">
                  Update
                </Button>
              </div>
            </div>

            <Button
              variant="danger"
              className="w-full"
              onClick={() => {
                setConnected(false);
                setActiveTerminal(null);
                setSuccess('Disconnected from MT5');
              }}
            >
              Disconnect
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};
