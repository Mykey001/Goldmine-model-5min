# Data Requirements for Goldmine ML Strategy

## Overview

This document specifies the exact data requirements needed to train and validate the Goldmine ML trading model.

---

## Required Data Specifications

### 1. Market Data (OHLCV)

#### Timeframes Needed
- **M1 (1-minute):** For immediate micro-trend swing analysis
- **M3 (3-minute):** For intermediate swing high/low detection  
- **M5 (5-minute):** Primary execution and signal generation timeframe
- **H1 (1-hour):** Macro-trend EMA filter validation

#### Data Points per Candle
```
timestamp    : datetime (ISO 8601 format: YYYY-MM-DD HH:MM:SS)
open         : float (opening price)
high         : float (highest price in period)
low          : float (lowest price in period)
close        : float (closing price)
volume       : float (tick volume or real volume)
```

#### File Naming Convention
```
{SYMBOL}_{TIMEFRAME}_{START_DATE}_to_{END_DATE}.csv

Examples:
- XAUUSD_M1_2024-01-01_to_2024-12-31.csv
- XAUUSD_M3_2024-01-01_to_2024-12-31.csv
- XAUUSD_M5_2024-01-01_to_2024-12-31.csv
- XAUUSD_H1_2024-01-01_to_2024-12-31.csv
```

#### CSV Format Example
```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,2063.45,2063.78,2063.12,2063.45,1250
2024-01-01 00:01:00,2063.45,2063.89,2063.34,2063.67,1420
2024-01-01 00:02:00,2063.67,2064.12,2063.56,2064.01,1680
```

### 2. Historical Data Depth

#### Minimum Requirements
- **Duration:** 6 months of continuous data
- **Start Date:** At least 180 days before present
- **Data Quality:** No gaps exceeding 5 consecutive candles
- **Market Conditions:** Must include trending, ranging, and volatile periods

#### Recommended Requirements  
- **Duration:** 12-24 months of continuous data
- **Reasoning:** More diverse market conditions for robust training
- **Market Cycles:** Include both bull and bear phases

### 3. Trading Symbol

**Primary Target:** Gold (XAUUSD)

**Alternative Symbols (if applicable):**
- Forex pairs: EURUSD, GBPUSD, USDJPY
- Other commodities: XAGUSD (Silver), USOIL (Oil)
- Indices: US30, NAS100, SPX500

**Note:** Strategy parameters may need adjustment for non-Gold symbols.

---

## Optional but Highly Valuable Data

### 1. Strategy Execution History (Ground Truth Labels)

If you have historical trades from running the original MQL5 EA:

```csv
trade_id,entry_timestamp,exit_timestamp,direction,entry_price,exit_price,lots,profit_usd,exit_reason
1,2024-01-15 08:30:00,2024-01-15 09:15:00,SELL,2068.45,2065.20,0.30,97.50,TP_HIT
2,2024-01-15 14:22:00,2024-01-15 14:45:00,BUY,2070.12,2071.80,0.30,50.40,TP_HIT
```

**Fields:**
- `trade_id`: Unique identifier
- `entry_timestamp`: When position opened
- `exit_timestamp`: When position closed
- `direction`: BUY or SELL
- `entry_price`: Entry price level
- `exit_price`: Exit price level
- `lots`: Position size
- `profit_usd`: Profit/loss in USD
- `exit_reason`: TP_HIT, SL_HIT, DAILY_LIMIT, MANUAL_CLOSE

**Value:** This provides supervised learning labels, dramatically improving model accuracy.

### 2. Additional Market Data

**Spread Data:**
```csv
timestamp,bid,ask,spread
2024-01-01 00:00:00,2063.42,2063.48,0.06
```

**Order Book Data (if available):**
- Bid/Ask volumes
- Depth of market
- Liquidity levels

---

## Data Export Instructions

### From MetaTrader 5 (MT5)

#### Method 1: Manual Export
1. Open MT5 platform
2. Open desired symbol chart
3. Press `F2` or go to View → Data Window
4. Right-click on chart → "Export to CSV"
5. Select date range and save file

#### Method 2: Using MT5 Python API
```python
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialize MT5
mt5.initialize()

# Define parameters
symbol = "XAUUSD"
timeframes = {
    'M1': mt5.TIMEFRAME_M1,
    'M3': mt5.TIMEFRAME_M3,
    'M5': mt5.TIMEFRAME_M5,
    'H1': mt5.TIMEFRAME_H1
}

# Date range
end_date = datetime.now()
start_date = end_date - timedelta(days=365)  # 1 year

# Export each timeframe
for tf_name, tf_code in timeframes.items():
    rates = mt5.copy_rates_range(symbol, tf_code, start_date, end_date)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.rename(columns={
        'time': 'timestamp',
        'tick_volume': 'volume'
    })
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df.to_csv(f'data/raw/{symbol}_{tf_name}_{start_date.date()}_to_{end_date.date()}.csv', index=False)

mt5.shutdown()
```

### From Other Sources

**Broker APIs:**
- Interactive Brokers API
- Oanda API
- FXCM API

**Data Providers:**
- TrueFX
- Dukascopy
- AlphaVantage
- Polygon.io

---

## Data Quality Checklist

Before providing data, ensure:

- [ ] All timestamps are in chronological order
- [ ] No duplicate timestamps
- [ ] OHLC relationships are valid: `low <= open <= high`, `low <= close <= high`
- [ ] No missing values (NaN)
- [ ] Volume values are positive
- [ ] Timezone is consistent (preferably UTC)
- [ ] Gaps in data are minimal (<1% of total candles)
- [ ] File encoding is UTF-8
- [ ] Decimal separator is period (.) not comma (,)

---

## Data Delivery

### Where to Place Files

Place all CSV files in the following directory:
```
Profitable5min/data/raw/
```

### File Size Considerations

Expected file sizes (approximate):
- M1 (1-minute) 1 year: ~500,000 rows → ~50 MB
- M3 (3-minute) 1 year: ~175,000 rows → ~18 MB
- M5 (5-minute) 1 year: ~105,000 rows → ~11 MB
- H1 (1-hour) 1 year: ~8,760 rows → ~1 MB

**Total:** ~80 MB for 1 year of 4 timeframes

### Compression (Optional)

If files are large, compress as:
- ZIP format: `XAUUSD_2024_data.zip`
- Place in `data/raw/` and extract

---

## Data Validation Script

After providing data, run this validation notebook:
```
notebooks/00_data_validation.ipynb
```

This will:
- Check file format and structure
- Validate data quality
- Identify gaps and issues
- Generate data summary report

---

## Questions?

If you have questions about:
1. **Data export:** See MT5 export instructions above
2. **File format:** Follow CSV example precisely
3. **Missing data:** Small gaps (<5 candles) will be interpolated
4. **Alternative symbols:** Confirm symbol specifications first

---

## Summary

**Minimum Required:**
- 4 CSV files (M1, M3, M5, H1)
- 6 months of XAUUSD data
- OHLCV columns with timestamp

**Recommended:**
- 12-24 months of data
- Historical trade logs from EA
- Spread data

**Next Step:** Once data is provided, we begin with `notebooks/01_data_exploration.ipynb`
