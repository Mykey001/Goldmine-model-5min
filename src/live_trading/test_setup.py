"""
Test script to verify setup and database connection
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required packages are installed"""
    logger.info("Testing imports...")
    
    try:
        import MetaTrader5 as mt5
        logger.info(f"✓ MetaTrader5 installed: {mt5.__version__}")
    except ImportError:
        logger.error("✗ MetaTrader5 not installed")
        return False
    
    try:
        import pandas as pd
        logger.info(f"✓ Pandas installed: {pd.__version__}")
    except ImportError:
        logger.error("✗ Pandas not installed")
        return False
    
    try:
        import xgboost as xgb
        logger.info(f"✓ XGBoost installed: {xgb.__version__}")
    except ImportError:
        logger.error("✗ XGBoost not installed")
        return False
    
    try:
        from fastapi import FastAPI
        logger.info("✓ FastAPI installed")
    except ImportError:
        logger.error("✗ FastAPI not installed")
        return False
    
    try:
        from sqlalchemy import create_engine
        logger.info("✓ SQLAlchemy installed")
    except ImportError:
        logger.error("✗ SQLAlchemy not installed")
        return False
    
    return True


def test_database():
    """Test database connection"""
    logger.info("Testing database connection...")
    
    try:
        from database.db_manager import DatabaseManager
        
        # Load environment variables
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            logger.error("✗ DATABASE_URL not set in environment")
            return False
        
        # Initialize database manager
        db = DatabaseManager(db_url)
        
        # Try to create tables
        if db.init_database():
            logger.info("✓ Database connection successful")
            logger.info("✓ Database tables created")
            return True
        else:
            logger.error("✗ Failed to create database tables")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False


def test_mt5_discovery():
    """Test MT5 terminal discovery"""
    logger.info("Testing MT5 terminal discovery...")
    
    try:
        from mt5_terminal_manager import MT5TerminalManager
        
        manager = MT5TerminalManager()
        terminals = manager.discover_terminals()
        
        if terminals:
            logger.info(f"✓ Found {len(terminals)} MT5 terminal(s)")
            for terminal in terminals:
                logger.info(f"  - {terminal['name']} ({terminal['broker']})")
            return True
        else:
            logger.warning("⚠ No MT5 terminals found (this is OK if MT5 is not installed)")
            return True
            
    except Exception as e:
        logger.error(f"✗ MT5 discovery test failed: {e}")
        return False


def test_model_file():
    """Test that trained model exists"""
    logger.info("Testing model file...")
    
    # Go up two directories to project root
    model_path = '../../models/final/xgboost_model.pkl'
    
    if os.path.exists(model_path):
        logger.info(f"✓ Model file found: {model_path}")
        
        try:
            import joblib
            model = joblib.load(model_path)
            logger.info(f"✓ Model loaded successfully: {type(model).__name__}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to load model: {e}")
            return False
    else:
        logger.warning(f"⚠ Model file not found: {model_path}")
        logger.warning("  Run model training scripts first")
        return False


def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("GOLDMINE ML LIVE TRADING - SETUP TEST")
    logger.info("="*60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Database Connection", test_database),
        ("MT5 Terminal Discovery", test_mt5_discovery),
        ("Model File", test_model_file),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Ready to start live trading system.")
    else:
        logger.warning("\n⚠ Some tests failed. Please fix issues before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
