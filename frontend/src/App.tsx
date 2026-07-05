import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Settings, ChevronLeft, ChevronRight } from 'lucide-react';
import { Header } from './components/layout/Header';
import { MetricsOverview } from './components/dashboard/MetricsOverview';
import { EquityCurve } from './components/dashboard/EquityCurve';
import { OpenPositions } from './components/dashboard/OpenPositions';
import { SignalHistory } from './components/dashboard/SignalHistory';
import { TradeHistory } from './components/dashboard/TradeHistory';
import { ConnectionPanel } from './components/controls/ConnectionPanel';
import { SettingsPanel } from './components/controls/SettingsPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { useDataFetcher } from './hooks/useDataFetcher';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Initialize WebSocket connection
  useWebSocket();

  // Fetch data from API
  useDataFetcher();

  return (
    <div className="min-h-screen bg-slate-900 flex">
      {/* Sidebar - Controls */}
      <div
        className={`${
          sidebarOpen ? 'w-96' : 'w-0'
        } transition-all duration-300 overflow-hidden bg-slate-800 border-r border-slate-700`}
      >
        <div className="p-6 space-y-6 overflow-y-auto h-screen">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-white">
              <Settings size={24} />
              <h2 className="text-xl font-bold">Controls</h2>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            >
              <ChevronLeft size={20} className="text-slate-400" />
            </button>
          </div>

          <ConnectionPanel />
          <SettingsPanel />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <Header />

        {/* Sidebar Toggle Button */}
        {!sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="fixed left-4 top-20 z-50 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg shadow-lg transition-colors"
            title="Open Controls"
          >
            <Settings size={20} className="text-white" />
          </button>
        )}

        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto px-6 py-8">
            {/* Metrics Overview */}
            <div className="mb-8 animate-fade-in">
              <MetricsOverview />
            </div>

            {/* Equity Curve */}
            <div className="mb-8 animate-fade-in" style={{ animationDelay: '0.1s' }}>
              <EquityCurve />
            </div>

            {/* Open Positions and Signal History */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
                <OpenPositions />
              </div>
              <div className="animate-fade-in" style={{ animationDelay: '0.3s' }}>
                <SignalHistory />
              </div>
            </div>

            {/* Trade History */}
            <div className="animate-fade-in" style={{ animationDelay: '0.4s' }}>
              <TradeHistory />
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-slate-800 border-t border-slate-700 py-6">
          <div className="container mx-auto px-6 text-center text-slate-400 text-sm">
            <p>Goldmine ML Trading Dashboard • Powered by ML & Real-time Data</p>
            <p className="mt-1">© 2026 - Automated Trading System</p>
          </div>
        </footer>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
