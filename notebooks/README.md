# Goldmine ML Strategy - Jupyter Notebooks

## 🎯 Project Workflow

Follow these notebooks in sequence:

1. **01_data_exploration.ipynb** ✅ - Load and validate market data
2. **02_feature_engineering.ipynb** ⏳ - Create 50+ ML features
3. **03_model_training.ipynb** 📅 - Train ML models
4. **04_model_evaluation.ipynb** 📅 - Evaluate performance
5. **05_backtesting.ipynb** 📅 - Backtest strategy

---

## 🚀 Jupyter is Running!

**Access at:** http://localhost:8889/tree?token=eb43640479e2744a7c6b0d4b04e55071a20811cbba42f74e

Your browser should have automatically opened. If not, copy the URL above.

---

## 📝 Current Status

### ✅ Completed
- [x] Project structure
- [x] Documentation
- [x] Data collection (1.37M candles)
- [x] Data exploration
- [x] Feature engineering modules (Python)

### ⏳ Next: Build Notebooks
- [ ] 02_feature_engineering.ipynb
- [ ] 03_model_training.ipynb
- [ ] 04_model_evaluation.ipynb
- [ ] 05_backtesting.ipynb

---

## 🛠️ How to Use

### In Jupyter Browser:

1. **Open a notebook** - Click on any `.ipynb` file
2. **Run cells** - Click in a cell, press `Shift + Enter`
3. **Add cells** - Press `B` for below, `A` for above
4. **Save** - `Ctrl + S` or File → Save

### Notebook Structure:

Each notebook will have:
- **Markdown cells** - Explanations and instructions
- **Code cells** - Python code to execute
- **Output cells** - Results, charts, tables

---

## 📊 02_feature_engineering.ipynb (Next)

This notebook will:

1. **Load Data** - M5 and H1 timeframes
2. **Calculate RSI(14)** - Core strategy indicator
3. **Detect Crossovers** - RSI signals (oversold/overbought)
4. **Calculate EMA(50)** - H1 macro trend filter
5. **Swing Detection** - Multi-timeframe alignment
6. **Volume Profile POC** - 24h institutional consensus
7. **Technical Indicators** - MACD, ATR, Bollinger Bands
8. **Temporal Features** - Trading sessions, time patterns
9. **Merge Timeframes** - Align H1 with M5
10. **Visualize** - Charts and analysis
11. **Save Features** - Export to CSV

**Expected Time:** 15-20 minutes (POC calculation is intensive)

---

## 💡 Tips for Building Notebooks

### Good Notebook Structure:

```markdown
# Title

## Section 1: Setup
[code cell: imports]
[code cell: load data]

## Section 2: Analysis
[markdown: explanation]
[code cell: calculation]
[code cell: visualization]

## Section 3: Results
[code cell: save output]
```

### Best Practices:

1. **One task per cell** - Don't cram everything into one cell
2. **Add markdown** - Explain what each section does
3. **Visualize often** - Charts help understand data
4. **Print progress** - Use `print()` to show status
5. **Save checkpoints** - Save important results to CSV
6. **Clear outputs** - Kernel → Restart & Clear Output before final save

---

## 🔧 Useful Jupyter Shortcuts

| Action | Shortcut |
|--------|----------|
| Run cell | `Shift + Enter` |
| Add cell below | `B` |
| Add cell above | `A` |
| Delete cell | `DD` |
| Cell to markdown | `M` |
| Cell to code | `Y` |
| Save notebook | `Ctrl + S` |
| Command mode | `Esc` |
| Edit mode | `Enter` |
| Restart kernel | `00` |

---

## 📁 File Organization

```
notebooks/
├── 01_data_exploration.ipynb        ✅ Complete
├── 02_feature_engineering.ipynb     ⏳ Build this next
├── 03_model_training.ipynb          📅 Future
├── 04_model_evaluation.ipynb        📅 Future
├── 05_backtesting.ipynb             📅 Future
│
├── data_exploration_script.py       (reference)
└── feature_engineering_script.py   (reference)
```

---

## 🎯 Feature Engineering Checklist

When building `02_feature_engineering.ipynb`, include:

### Core Strategy Features:
- [ ] RSI(14) calculation
- [ ] RSI crossover detection (35.0 oversold, 65.0 overbought)
- [ ] H1 EMA(50) calculation
- [ ] Price vs EMA comparison
- [ ] Volume Profile POC (24h)
- [ ] Price vs POC comparison
- [ ] Swing highs/lows (M1, M3, M5)
- [ ] Multi-timeframe alignment

### Additional Features:
- [ ] ATR(14) - Volatility
- [ ] MACD - Momentum
- [ ] Bollinger Bands - Volatility bands
- [ ] Price action (momentum, ROC)
- [ ] Temporal features (hour, day, session)
- [ ] Volume features

### Outputs:
- [ ] Visualizations (RSI, POC, trends)
- [ ] Feature correlation heatmap
- [ ] Save to `data/features/features_M5_complete.csv`
- [ ] Feature metadata CSV

---

## 📚 Reference Materials

**In Project:**
- `docs/Goldmine_Strategy_Theory.md` - Strategy psychology
- `docs/Project_Plan.md` - Complete pipeline
- `docs/Data_Exploration_Results.md` - Data analysis
- `src/feature_engineering/` - Python modules to use

**Python Scripts (Reference):**
- `data_exploration_script.py` - See data loading example
- `feature_engineering_script.py` - See feature calculation example

You can run these scripts to see expected output, then build interactive notebooks.

---

## 🚨 Important Notes

1. **Don't commit large files** - Use `.gitignore` for CSVs
2. **Clear outputs before committing** - Kernel → Restart & Clear Output
3. **Save frequently** - Jupyter can crash
4. **Comment your code** - Future you will thank you
5. **Test with small samples first** - Use `.head(1000)` for testing

---

## 🔄 Workflow

### Development Cycle:

```
1. Open notebook
   ↓
2. Write markdown (explain what you'll do)
   ↓
3. Write code cell
   ↓
4. Run cell (Shift+Enter)
   ↓
5. Check output
   ↓
6. Add visualization if helpful
   ↓
7. Save (Ctrl+S)
   ↓
8. Repeat from step 2
```

### When Complete:

```
1. Kernel → Restart & Run All
2. Check for errors
3. Save notebook
4. Commit to git (with cleared outputs)
```

---

## 🆘 Troubleshooting

### Kernel won't start
**Solution:** Restart Jupyter server (Ctrl+C in terminal, then restart)

### Module not found
**Solution:** Add to first cell:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent / 'src'))
```

### Out of memory
**Solution:** Process data in chunks or use smaller samples

### Cell runs forever
**Solution:** Kernel → Interrupt (stop button)

---

## 🎉 Ready to Build!

**Next Steps:**

1. ✅ Jupyter is running (check browser)
2. 📖 Review `docs/Project_Plan.md` for feature details
3. 🔍 Look at `src/feature_engineering/` modules
4. 📝 Open `02_feature_engineering.ipynb`
5. 🚀 Start building step by step!

**You have all the Python modules ready in `src/` - just import and use them in your notebook!**

---

**Happy coding!** 🎯
