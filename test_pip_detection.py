"""
Test script to verify pip value auto-detection
"""

# Simulate the TradeExecutor pip detection logic
# Note: For gold, 1 pip = 10 points on most platforms
SYMBOL_PIP_SIZES = {
    # Gold (1 pip = 10 points)
    'XAUUSD': 0.1,
    'XAUUSDm': 0.1,
    'GOLD': 0.1,
    
    # Silver
    'XAGUSD': 0.001,
    'XAGUSDm': 0.001,
    'SILVER': 0.001,
    
    # JPY pairs (2 decimal places)
    'USDJPY': 0.01,
    'EURJPY': 0.01,
    'GBPJPY': 0.01,
    
    # Most forex pairs (4 decimal places)
    'EURUSD': 0.0001,
    'GBPUSD': 0.0001,
    'AUDUSD': 0.0001,
    
    # Crypto
    'BTCUSD': 1.0,
    'ETHUSD': 0.1,
}

def detect_pip_value(symbol: str) -> float:
    """Auto-detect pip value based on symbol"""
    clean_symbol = symbol.upper()
    for suffix in ['M', '.RAW', '.', '_']:
        if suffix in clean_symbol:
            clean_symbol = clean_symbol.split(suffix)[0]
    
    if symbol.upper() in SYMBOL_PIP_SIZES:
        return SYMBOL_PIP_SIZES[symbol.upper()]
    
    if clean_symbol in SYMBOL_PIP_SIZES:
        return SYMBOL_PIP_SIZES[clean_symbol]
    
    if 'JPY' in clean_symbol or 'HUF' in clean_symbol:
        return 0.01
    elif 'XAU' in clean_symbol or 'GOLD' in clean_symbol:
        return 0.1
    elif 'XAG' in clean_symbol or 'SILVER' in clean_symbol:
        return 0.001
    elif 'BTC' in clean_symbol or 'ETH' in clean_symbol:
        return 1.0
    else:
        return 0.0001

def test_pip_detection():
    """Test pip value detection for various symbols"""
    
    # Configuration - BACK TO NORMAL VALUES (Gold pip multiplier fixed)
    TP_PIPS = 100
    SL_PIPS = 50
    
    test_cases = [
        # Symbol, Expected Pip Value
        ('XAUUSDm', 0.1),  # Gold: 1 pip = 10 points
        ('XAUUSD', 0.1),   # Gold: 1 pip = 10 points
        ('EURUSD', 0.0001),  # Standard forex
        ('GBPUSD', 0.0001),  # Standard forex
        ('USDJPY', 0.01),   # JPY pair
        ('EURJPY', 0.01),   # JPY pair
        ('XAGUSD', 0.001), # Silver
        ('BTCUSD', 1.0),   # Bitcoin
    ]
    
    print("\n" + "="*80)
    print("PIP VALUE AUTO-DETECTION TEST")
    print("="*80)
    print(f"\nConfiguration: TP_PIPS={TP_PIPS}, SL_PIPS={SL_PIPS}\n")
    
    all_passed = True
    
    for symbol, expected_pip in test_cases:
        print(f"\nTesting: {symbol}")
        print("-" * 40)
        
        # Detect pip value
        pip_value = detect_pip_value(symbol)
        
        # Check pip value
        if pip_value == expected_pip:
            print(f"✓ Pip Value: {pip_value} (CORRECT)")
        else:
            print(f"✗ Pip Value: {pip_value} (EXPECTED: {expected_pip})")
            all_passed = False
        
        # Calculate actual points
        sl_points = SL_PIPS * pip_value
        tp_points = TP_PIPS * pip_value
        
        print(f"  Stop Loss: {SL_PIPS} pips = {sl_points} points")
        print(f"  Take Profit: {TP_PIPS} pips = {tp_points} points")
        
        # Example trade for gold
        if symbol in ['XAUUSDm', 'XAUUSD']:
            entry_price = 4153.269
            print(f"\n  Example BUY trade at {entry_price}:")
            print(f"    Entry: {entry_price}")
            print(f"    Stop Loss: {entry_price - sl_points:.3f} ({sl_points} points = {SL_PIPS} pips below)")
            print(f"    Take Profit: {entry_price + tp_points:.3f} ({tp_points} points = {TP_PIPS} pips above)")
            print(f"\n  💰 Risk/Reward with 0.01 lot:")
            print(f"    Risk: ${sl_points * 0.01 * 100:.2f}")
            print(f"    Reward: ${tp_points * 0.01 * 100:.2f}")
            print(f"\n  ⚠️  OLD BEHAVIOR (PIP_VALUE=0.01, treating pip as $0.01):")
            old_sl = 0.5  # 50 * 0.01
            print(f"    Old Stop Loss: {entry_price - old_sl:.3f} (only {old_sl} points - TOO TIGHT!)")
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    test_pip_detection()
