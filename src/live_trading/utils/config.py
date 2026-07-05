"""
Configuration management
"""
import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration"""
    
    def __init__(self):
        """Load configuration from environment"""
        load_dotenv()
        
        # Database
        self.DATABASE_URL = os.getenv('DATABASE_URL')
        
        # API
        self.API_HOST = os.getenv('API_HOST', '0.0.0.0')
        self.API_PORT = int(os.getenv('API_PORT', 8000))
        self.API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'change-this-secret-key')
        self.CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
        
        # Risk Management
        self.MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 400))
        self.MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', 1))
        self.MIN_CONFIDENCE = float(os.getenv('MIN_CONFIDENCE', 0.5))
        self.DEFAULT_LOT_SIZE = float(os.getenv('DEFAULT_LOT_SIZE', 0.01))
        
        # Trading Parameters
        self.TP_PIPS = float(os.getenv('TP_PIPS', 100))
        self.SL_PIPS = float(os.getenv('SL_PIPS', 50))
        self.PIP_VALUE = float(os.getenv('PIP_VALUE', 0.01))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/live_trading.log')
        
        # Model
        self.MODEL_PATH = os.getenv('MODEL_PATH', 'models/final/xgboost_model.pkl')
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid, False otherwise
        """
        if not self.DATABASE_URL:
            print("ERROR: DATABASE_URL not set")
            return False
        
        if not os.path.exists(self.MODEL_PATH):
            print(f"WARNING: Model file not found: {self.MODEL_PATH}")
            # Don't fail - model might be trained later
        
        return True
    
    def __repr__(self):
        """String representation (hide sensitive data)"""
        return f"<Config(API_PORT={self.API_PORT}, MAX_DAILY_LOSS={self.MAX_DAILY_LOSS})>"


# Global config instance
config = Config()
