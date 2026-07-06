"""
Verification script to check if all fixes are correctly applied
"""
import os
import sys
import json

print("="*60)
print("VERIFICATION SCRIPT - Checking Fixes")
print("="*60)

all_passed = True

# Test 1: Check feature_names.json exists and has correct content
print("\n[1/3] Checking feature_names.json...")
feature_file = os.path.join('data', 'features', 'feature_names.json')
if not os.path.exists(feature_file):
    print("  ❌ FAIL: feature_names.json not found at", feature_file)
    all_passed = False
else:
    with open(feature_file, 'r') as f:
        features = json.load(f)
    
    expected_count = 38
    if len(features) != expected_count:
        print(f"  ❌ FAIL: Expected {expected_count} features, got {len(features)}")
        all_passed = False
    else:
        print(f"  ✓ PASS: Correct feature count ({expected_count})")
    
    # Check for OHLCV columns (should NOT be present)
    ohlcv_cols = ['date', 'time', 'open', 'high', 'low', 'close', 'tickvol', 'vol', 'spread']
    found_ohlcv = [col for col in ohlcv_cols if col in features]
    if found_ohlcv:
        print(f"  ❌ FAIL: Found OHLCV columns that should be excluded: {found_ohlcv}")
        all_passed = False
    else:
        print("  ✓ PASS: No OHLCV columns present")
    
    # Check for required feature groups
    required_features = {
        'RSI': ['rsi', 'rsi_oversold', 'rsi_overbought'],
        'Volume': ['volume_ma', 'volume_ratio', 'volume_surge'],
        'Temporal': ['hour', 'day_of_week', 'day_of_month', 'week_of_year'],
        'Sessions': ['session_asian', 'session_european', 'session_us']
    }
    
    for group, feature_list in required_features.items():
        missing = [f for f in feature_list if f not in features]
        if missing:
            print(f"  ❌ FAIL: Missing {group} features: {missing}")
            all_passed = False
        else:
            print(f"  ✓ PASS: {group} features present")

# Test 2: Check signal_generator.py has correct path resolution
print("\n[2/3] Checking signal_generator.py path resolution...")
sig_gen_file = os.path.join('src', 'live_trading', 'signal_generator.py')
if not os.path.exists(sig_gen_file):
    print("  ❌ FAIL: signal_generator.py not found")
    all_passed = False
else:
    with open(sig_gen_file, 'r') as f:
        content = f.read()
    
    # Check for the fixed path resolution code
    if 'project_root = os.path.dirname(os.path.dirname(os.path.dirname' in content:
        print("  ✓ PASS: Path resolution code found")
    else:
        print("  ❌ FAIL: Path resolution code not found (relative path issue not fixed)")
        all_passed = False
    
    # Check that old filtering logic is removed
    if 'exclude_cols = [' in content and 'all_cols = json.load' in content:
        print("  ❌ FAIL: Old filtering logic still present")
        all_passed = False
    else:
        print("  ✓ PASS: Old filtering logic removed")

# Test 3: Check rest_api.py has executor null checks
print("\n[3/3] Checking rest_api.py executor null checks...")
api_file = os.path.join('src', 'live_trading', 'api', 'rest_api.py')
if not os.path.exists(api_file):
    print("  ❌ FAIL: rest_api.py not found")
    all_passed = False
else:
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Check for executor null checks
    checks = [
        'if bot.executor is None:',
        'return []  # Return empty list if executor not initialized',
    ]
    
    found = sum(1 for check in checks if check in content)
    if found >= 2:
        print("  ✓ PASS: Executor null checks found")
    else:
        print(f"  ❌ FAIL: Executor null checks not complete (found {found}/2)")
        all_passed = False

# Final result
print("\n" + "="*60)
if all_passed:
    print("✅ ALL CHECKS PASSED!")
    print("\nYou can now:")
    print("1. Restart the trading bot backend")
    print("2. Refresh the frontend")
    print("3. System should work without errors")
else:
    print("❌ SOME CHECKS FAILED")
    print("\nPlease review the failures above")
print("="*60)

sys.exit(0 if all_passed else 1)
