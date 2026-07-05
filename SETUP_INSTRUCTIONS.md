# 🚀 Goldmine ML Live Trading - Setup Instructions

## Phase 1: Backend Setup (In Progress)

### Step 1: Install Dependencies

```bash
# Make sure you're in the project root
cd C:\Users\MYCkey98\Desktop\Organized_Files\05_ML_Projects\Profitable5min

# Create/activate virtual environment (if not already done)
python -m venv venv
venv\Scripts\activate

# Install live trading dependencies
pip install -r requirements-live.txt
```

### Step 2: Initialize Database

The PostgreSQL database is already configured in `.env` file. Now we need to create the tables:

```bash
# Navigate to live trading directory
cd src\live_trading

# Run setup test (this will also create database tables)
python test_setup.py
```

Expected output:
```
✓ Package Imports - PASS
✓ Database Connection - PASS  
✓ MT5 Terminal Discovery - PASS (or WARNING if MT5 not installed)
✓ Model File - PASS (or WARNING if model not trained yet)
```

### Step 3: Verify Setup

If you see any failures:

**Package Imports Failed:**
```bash
pip install -r requirements-live.txt --upgrade
```

**Database Connection Failed:**
- Check internet connection
- Verify DATABASE_URL in `.env` file
- Check if password is correct

**MT5 Terminal Discovery:**
- This is optional for now
- Will be needed when you want to connect to MT5

**Model File Missing:**
- Train the model first using: `python scripts/03_model_training.py`

---

## Current Progress ✅

**Completed:**
- [x] Project structure created
- [x] Database models defined (PostgreSQL)
- [x] Database manager implemented
- [x] MT5 Terminal Manager implemented
- [x] Environment configuration
- [x] Setup test script

**Next Steps:**
1. Run `python src/live_trading/test_setup.py` to verify setup
2. Create remaining modules (signal generator, trade executor, etc.)
3. Build REST API
4. Build WebSocket server
5. Create React frontend

---

## File Structure Created

```
Profitable5min/
├── src/
│   └── live_trading/
│       ├── __init__.py
│       ├── mt5_terminal_manager.py  ✅ Created
│       ├── test_setup.py            ✅ Created
│       ├── database/
│       │   ├── __init__.py          ✅ Created
│       │   ├── models.py            ✅ Created
│       │   └── db_manager.py        ✅ Created
│       ├── api/                     ⏳ Next
│       └── utils/                   ⏳ Next
├── .env                             ✅ Created
├── .env.example                     ✅ Created
├── requirements-live.txt            ✅ Created
└── SETUP_INSTRUCTIONS.md            ✅ Created
```

---

## Quick Command Reference

```bash
# Activate environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements-live.txt

# Test setup
cd src\live_trading
python test_setup.py

# Check database tables (optional)
# You can use any PostgreSQL client to connect and verify tables were created
```

---

## Database Tables Created

When you run the setup, these tables will be created in PostgreSQL:

1. **trades** - All trade records (open and closed)
2. **signals** - ML signal history
3. **account_snapshots** - Account balance snapshots
4. **daily_summary** - Daily performance summaries

---

## Troubleshooting

### Issue: pip install fails
**Solution:** Make sure you have Python 3.10+ installed
```bash
python --version
```

### Issue: Database connection fails
**Solution:** Check your internet connection and verify the DATABASE_URL

### Issue: MetaTrader5 package fails to install
**Solution:** This is Windows-only. Make sure you're on Windows 10/11
```bash
pip install --upgrade MetaTrader5
```

### Issue: psycopg2 fails to install
**Solution:** Use the binary version:
```bash
pip uninstall psycopg2
pip install psycopg2-binary
```

---

## Next: Run Test

After installation, run the test:

```bash
cd src\live_trading
python test_setup.py
```

If all tests pass, you're ready for the next phase! 🎉
