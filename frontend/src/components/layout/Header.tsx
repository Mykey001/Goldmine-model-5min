import React from 'react';
import { Activity, Wifi, WifiOff, Server } from 'lucide-react';
import { useConnectionStore } from '../../store/connectionStore';
import { useAccountStore } from '../../store/accountStore';

export const Header: React.FC = () => {
  const { isConnected, isWSConnected, activeTerminal, currentSymbol } = useConnectionStore();
  const account = useAccountStore((state) => state.account);

  return (
    <header className="bg-slate-800 border-b border-slate-700 shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
              <Activity size={28} className="text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                Goldmine ML Trading
              </h1>
              <p className="text-sm text-slate-400">
                Automated Trading Dashboard
              </p>
            </div>
          </div>

          {/* Connection Status and Info */}
          <div className="flex items-center gap-6">
            {/* Symbol Info */}
            {currentSymbol && (
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-700 rounded-lg">
                <Server size={16} className="text-blue-400" />
                <div className="text-sm">
                  <div className="text-slate-400">Trading</div>
                  <div className="text-white font-semibold">{currentSymbol}</div>
                </div>
              </div>
            )}

            {/* Account Info */}
            {account && (
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-700 rounded-lg">
                <div className="text-sm">
                  <div className="text-slate-400">Account #{account.account}</div>
                  <div className="text-white font-semibold">{account.server}</div>
                </div>
              </div>
            )}

            {/* Connection Status */}
            <div className="flex items-center gap-4">
              {/* MT5 Connection */}
              <div className="flex items-center gap-2">
                {isConnected ? (
                  <>
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse-slow" />
                    <span className="text-sm text-green-400 font-medium">MT5 Connected</span>
                  </>
                ) : (
                  <>
                    <div className="w-3 h-3 bg-red-500 rounded-full" />
                    <span className="text-sm text-red-400 font-medium">MT5 Disconnected</span>
                  </>
                )}
              </div>

              {/* WebSocket Connection */}
              <div className="flex items-center gap-2">
                {isWSConnected ? (
                  <Wifi size={20} className="text-green-400" />
                ) : (
                  <WifiOff size={20} className="text-red-400" />
                )}
                <span className="text-sm text-slate-400">
                  {isWSConnected ? 'Live' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
