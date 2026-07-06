# Quick Optimization Guide - Testing Different Filter Settings

## 🎯 Goal
Find the optimal balance between trade quality and absolute profit.

## 📊 Current Results

| Configuration | Trades | Win Rate | Profit Factor | Net Profit | Return % | Sharpe |
|--------------|--------|----------|---------------|------------|----------|--------|
| **No Filter** | 43,900 | 66.32% | 3.94 | $217,225 | 2,172% | 6.36 |
| **EMA-200 Filter** | 18,211 | 69.17% | 4.49 | $97,900 | 979% | 8.33 |

## 🧪 Recommended Tests

### Test 1: EMA-50 (Fast Trend Following)

**Edit config:**
```bash
notepad configs\backtest_config.yaml
```

Change to:
```yaml
trend_filter:
  enabled: true
  h1_ema_period: 50  # Fast
```

**Run:**
```bash
python scripts\05b_backtest_comparison.py
```

**Expected:**
- More trades than EMA-200
- Lower than no filter
- Win rate: ~67-68%
- Profit: Higher than EMA-200, lower than no filter

---

### Test 2: EMA-100 (Balanced)

**Edit config:**
```yaml
trend_filter:
  enabled: true
  h1_ema_period: 100  # Balanced
```

**Run:**
```bash
python scripts\05b_backtest_comparison.py
```

**Expected:**
- Moderate trade count (~25-30K)
- Win rate: ~67.5-68.5%
- Profit: $130-160K
- Good balance point

---

### Test 3: EMA-150 (Conservative)

**Edit config:**
```yaml
trend_filter:
  enabled: true
  h1_ema_period: 150  # Conservative
```

**Run:**
```bash
python scripts\05b_backtest_comparison.py
```

**Expected:**
- Trade count: ~20-22K
- Win rate: ~68-69%
- Profit: $100-120K

---

### Test 4: Higher Confidence Threshold (No Filter)

**Edit config:**
```yaml
trend_filter:
  enabled: false

signals:
  min_confidence: 0.6  # Increase from 0.5
```

**Run:**
```bash
python scripts\05b_backtest_comparison.py
```

**Expected:**
- Fewer trades than current no-filter
- Higher win rate
- Similar or better profit factor

---

### Test 5: Hybrid Approach

**Edit config:**
```yaml
trend_filter:
  enabled: true
  h1_ema_period: 100

signals:
  min_confidence: 0.55  # Slight increase
```

**Run:**
```bash
python scripts\05b_backtest_comparison.py
```

**Expected:**
- Combined filtering effect
- Better quality than no filter
- Higher profit than EMA-200 alone

---

## 📝 Result Tracking Template

Create a spreadsheet to track results:

| Test # | EMA Period | Min Conf | Trades | Win Rate | PF | Net Profit | Return % | Sharpe | Notes |
|--------|-----------|----------|--------|----------|-------|-----------|----------|--------|-------|
| 1 | None | 0.50 | 43,900 | 66.32% | 3.94 | $217,225 | 2,172% | 6.36 | Baseline |
| 2 | 200 | 0.50 | 18,211 | 69.17% | 4.49 | $97,900 | 979% | 8.33 | Too conservative |
| 3 | 50 | 0.50 | ??? | ??? | ??? | ??? | ??? | ??? | Test this |
| 4 | 100 | 0.50 | ??? | ??? | ??? | ??? | ??? | ??? | Test this |
| 5 | 150 | 0.50 | ??? | ??? | ??? | ??? | ??? | ??? | Test this |
| 6 | None | 0.60 | ??? | ??? | ??? | ??? | ??? | ??? | Test this |
| 7 | 100 | 0.55 | ??? | ??? | ??? | ??? | ??? | ??? | Test this |

---

## 🎯 Optimization Strategy

### Phase 1: Find Optimal EMA Period
1. Test EMA-50, 100, 150, 200
2. Plot: EMA Period vs Net Profit
3. Find the "sweet spot" where:
   - Win rate improves by 1-2%
   - Profit doesn't drop more than 20-30%

### Phase 2: Optimize Confidence Threshold
1. Take best EMA from Phase 1
2. Test min_confidence: 0.50, 0.55, 0.60, 0.65
3. Find threshold that maximizes profit factor

### Phase 3: Combine Best Settings
1. Combine optimal EMA + optimal confidence
2. Run final comparison
3. Validate on different time periods

---

## 🚀 Quick Test Script

Save this to `test_configs.bat`:

```batch
@echo off
echo Testing EMA-50...
python scripts\05_backtesting.py > results\ema50_test.txt

echo Testing EMA-100...
REM Edit config here
python scripts\05_backtesting.py > results\ema100_test.txt

echo Testing EMA-150...
REM Edit config here
python scripts\05_backtesting.py > results\ema150_test.txt

echo All tests complete!
```

Or use PowerShell for automation:

```powershell
# test_ema_periods.ps1
$ema_periods = @(50, 100, 150, 200)

foreach ($ema in $ema_periods) {
    Write-Host "Testing EMA-$ema..." -ForegroundColor Green
    
    # Update config
    $config = Get-Content "configs\backtest_config.yaml"
    $config = $config -replace "h1_ema_period: \d+", "h1_ema_period: $ema"
    $config | Set-Content "configs\backtest_config.yaml"
    
    # Run backtest
    python scripts\05_backtesting.py
    
    # Copy results
    Copy-Item "results\metrics\backtest_metrics.json" "results\ema${ema}_metrics.json"
    
    Write-Host "EMA-$ema complete!" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "All tests complete! Check results\ folder" -ForegroundColor Green
```

---

## 📊 Expected Optimization Curve

```
Net Profit vs EMA Period

$220K |  ●  (No filter)
     |
$180K |      ●  (EMA-50)
     |
$140K |          ●  (EMA-100)  ← Sweet spot?
     |
$100K |              ●  (EMA-150)
     |
 $60K |                  ●  (EMA-200)
      +-----|-----|-----|-----|-----
           None   50   100  150  200
                 EMA Period
```

Target: **EMA-100** likely gives ~$140-160K profit with ~68% win rate

---

## 💡 Pro Tips

1. **Run comparisons, not single backtests**
   - Always use `05b_backtest_comparison.py`
   - Shows side-by-side impact

2. **Focus on Sharpe Ratio**
   - Higher Sharpe = Better risk-adjusted returns
   - More important than absolute profit for scalability

3. **Consider transaction costs**
   - Higher frequency = Higher costs
   - Factor in spreads and commissions

4. **Test on different periods**
   - Bull markets
   - Bear markets
   - Ranging markets

5. **Use version control**
   - Save each config version
   - Document what works

---

## 🎯 Target Metrics

Based on your baseline results, aim for:

| Metric | Target | Why |
|--------|--------|-----|
| **Trades** | 25,000-30,000 | 30-40% reduction from baseline |
| **Win Rate** | 67-68% | 1-2% improvement |
| **Profit Factor** | 4.0-4.3 | Modest improvement |
| **Net Profit** | $150,000-$180,000 | 70-80% of baseline |
| **Sharpe Ratio** | 7.0-7.5 | 10-20% improvement |

This would give you **better quality without sacrificing too much profit**.

---

## ✅ Action Plan

**Today:**
1. Test EMA-100
2. Compare results

**This Week:**
1. Test EMA-50, 100, 150
2. Find optimal EMA period
3. Test confidence thresholds

**Next Week:**
1. Combine best settings
2. Validate on different time periods
3. Document final configuration
4. Prepare for live trading

---

## 📞 Results Interpretation Guide

### Good Signs ✅
- Win rate increases by 1-3%
- Profit factor increases by 0.2-0.5
- Sharpe ratio increases by 10-30%
- Net profit stays above 70% of baseline
- Max drawdown stays low (<5%)

### Warning Signs ⚠️
- Win rate increases but profit drops >50%
- Trade count drops >70%
- Sharpe decreases
- Max drawdown increases significantly

### Red Flags 🚫
- Win rate decreases
- Profit factor decreases
- No trades executed
- System errors

---

## 🎉 Success Criteria

You've found the optimal configuration when:
1. ✅ Win rate improves by at least 1%
2. ✅ Profit stays above 70% of baseline
3. ✅ Sharpe ratio improves
4. ✅ Trade count is manageable (not too high/low)
5. ✅ Results are consistent across time periods

**Then**: Deploy to live trading with small position sizes!

---

**Remember:** The goal is finding YOUR optimal balance between quality and quantity, not chasing perfect metrics.
