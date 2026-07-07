"""
Quick test script to verify MT5 data availability
Run this to check if MT5 can provide data for your date range
"""
import MetaTrader5 as mt5
from datetime import datetime

# Initialize MT5
if not mt5.initialize():
    print("❌ Failed to initialize MT5")
    print(f"Error: {mt5.last_error()}")
    exit()

print("✅ MT5 initialized")
print(f"Terminal: {mt5.terminal_info()}")
print()

# Test symbol
symbol = "XAUUSDm"
print(f"Testing symbol: {symbol}")

symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"❌ Symbol {symbol} not found")
    mt5.shutdown()
    exit()

print(f"✅ Symbol found: {symbol_info.name}")
print(f"   Visible: {symbol_info.visible}")
print(f"   Digits: {symbol_info.digits}")
print()

# Try to enable symbol if not visible
if not symbol_info.visible:
    print("Enabling symbol...")
    if mt5.symbol_select(symbol, True):
        print("✅ Symbol enabled")
    else:
        print("❌ Failed to enable symbol")
print()

# Test different date ranges
test_ranges = [
    ("Recent (Last 30 days)", datetime(2026, 6, 1), datetime(2026, 7, 6)),
    ("2 months ago", datetime(2026, 4, 1), datetime(2026, 5, 31)),
    ("Early 2026", datetime(2026, 1, 1), datetime(2026, 1, 31)),
    ("Late 2025", datetime(2025, 11, 1), datetime(2025, 11, 30)),
    ("Mid 2025", datetime(2025, 6, 1), datetime(2025, 6, 30)),
    ("Early 2025", datetime(2025, 1, 1), datetime(2025, 1, 31)),
]

print("Testing data availability for different date ranges:")
print("=" * 70)

for label, start, end in test_ranges:
    print(f"\n{label}: {start.date()} to {end.date()}")
    
    # Try M5 timeframe
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start, end)
    
    if rates is not None and len(rates) > 0:
        print(f"   ✅ M5 Data: {len(rates)} candles")
        print(f"   First: {datetime.fromtimestamp(rates[0]['time'])}")
        print(f"   Last:  {datetime.fromtimestamp(rates[-1]['time'])}")
    else:
        error = mt5.last_error()
        print(f"   ❌ No M5 data available. Error: {error}")

print("\n" + "=" * 70)
print("\n💡 Recommendation:")
print("   Use a date range that shows ✅ with plenty of candles (1000+)")
print("   This ensures your backtest has enough data to work with.")

# Shutdown
mt5.shutdown()
print("\n✅ Test complete")
