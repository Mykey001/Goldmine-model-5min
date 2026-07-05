# Goldmine ML Trading Dashboard

A modern, real-time trading dashboard built with React, TypeScript, and Vite for the Goldmine ML Trading System.

## 🎨 Features

- **Real-time Updates**: WebSocket integration for live trading data
- **Beautiful UI**: Modern design with Tailwind CSS
- **Interactive Charts**: Equity curve visualization with Recharts
- **Comprehensive Metrics**: Win rate, profit factor, P&L tracking
- **Live Positions**: Real-time position monitoring with P&L updates
- **Signal History**: Track all ML-generated trading signals
- **Trade History**: Complete log of closed trades
- **Responsive Design**: Works on desktop and tablet devices

## 🛠️ Tech Stack

- **React 19** - UI library
- **TypeScript 6** - Type safety
- **Vite 8** - Build tool & dev server
- **Tailwind CSS 4** - Styling
- **TanStack Query** - Data fetching & caching
- **Zustand** - State management
- **Socket.IO Client** - WebSocket communication
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Axios** - HTTP client

## 📦 Installation

```bash
# Install dependencies
npm install

# Or use yarn
yarn install
```

## 🚀 Development

```bash
# Start development server
npm run dev

# The app will be available at http://localhost:5173
```

## 🏗️ Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

For production, update these URLs to your production backend.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/        # Dashboard components
│   │   │   ├── MetricsOverview.tsx
│   │   │   ├── EquityCurve.tsx
│   │   │   ├── OpenPositions.tsx
│   │   │   ├── SignalHistory.tsx
│   │   │   └── TradeHistory.tsx
│   │   ├── layout/           # Layout components
│   │   │   └── Header.tsx
│   │   └── ui/               # Reusable UI components
│   │       ├── Card.tsx
│   │       ├── Badge.tsx
│   │       └── Button.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useWebSocket.ts
│   │   └── useDataFetcher.ts
│   ├── services/             # API & WebSocket services
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── store/                # Zustand stores
│   │   ├── accountStore.ts
│   │   ├── tradesStore.ts
│   │   ├── metricsStore.ts
│   │   └── connectionStore.ts
│   ├── types/                # TypeScript types
│   │   └── index.ts
│   ├── utils/                # Utility functions
│   │   └── formatters.ts
│   ├── App.tsx               # Main app component
│   ├── main.tsx              # Entry point
│   └── index.css             # Global styles
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🎯 Key Components

### MetricsOverview
Displays key performance metrics:
- Account Balance
- Today's P&L
- Win Rate
- Profit Factor

### EquityCurve
Interactive line chart showing:
- Equity over time
- Balance over time
- Hover tooltips with details

### OpenPositions
Real-time position monitoring:
- Symbol, direction, entry price
- Current price and P&L
- TP/SL levels
- Quick close button

### SignalHistory
Track ML signals:
- BUY/SELL/HOLD signals
- Confidence scores
- Execution status
- Timestamps

### TradeHistory
Complete trade log:
- Entry/exit prices
- Duration
- Profit/loss
- Execution times

## 🔌 API Integration

The dashboard connects to the backend API at `http://localhost:8000`:

### REST API Endpoints
- `GET /api/account/info` - Account information
- `GET /api/positions/open` - Open positions
- `GET /api/trades/history` - Trade history
- `GET /api/signals/history` - Signal history
- `GET /api/metrics/summary` - Performance metrics
- `GET /api/metrics/daily` - Daily metrics
- `GET /api/metrics/equity_curve` - Equity curve data
- `POST /api/positions/close/:ticket` - Close position

### WebSocket Events
- `trade_opened` - New trade opened
- `trade_closed` - Trade closed
- `new_signal` - New ML signal generated
- `account_update` - Account balance updated
- `metrics_update` - Metrics updated
- `position_update` - Position P&L updated

## 🎨 Customization

### Colors
Edit `tailwind.config.js` to customize the color scheme:

```js
theme: {
  extend: {
    colors: {
      primary: { ... },
    },
  },
}
```

### Polling Intervals
Edit `src/hooks/useDataFetcher.ts` to adjust data refresh rates:

```typescript
refetchInterval: 2000,  // 2 seconds
```

## 📊 Data Flow

```
Backend API → TanStack Query → Zustand Store → React Components
Backend WS → Socket.IO → Zustand Store → React Components
```

1. **TanStack Query** fetches initial data and handles caching
2. **WebSocket** provides real-time updates
3. **Zustand stores** manage application state
4. **React components** subscribe to stores and render UI

## 🐛 Debugging

### Check WebSocket Connection
Open browser console and look for:
```
WebSocket connected
```

### Check API Connection
Verify backend is running:
```bash
curl http://localhost:8000/api/health
```

### Enable React Query DevTools
Add to `App.tsx`:
```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<ReactQueryDevtools initialIsOpen={false} />
```

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel
```bash
vercel
```

### Deploy to Netlify
```bash
netlify deploy --prod
```

### Environment Variables
Remember to set production environment variables:
- `VITE_API_URL` - Production API URL
- `VITE_WS_URL` - Production WebSocket URL

## 📝 License

Part of the Goldmine ML Trading System

## 🤝 Support

For issues or questions, please check the main project documentation.
