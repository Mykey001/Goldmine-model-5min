"""
Launcher script - Start both trading bot and API server
"""
import os
import sys
import asyncio
import logging
import threading
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv

from main import LiveTradingBot
from api.rest_api import app, init_api
from api.websocket_server import ws_manager, websocket_endpoint
from utils.logger import setup_logger
from utils.config import config

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger('run', config.LOG_FILE, config.LOG_LEVEL)


def run_trading_bot(bot: LiveTradingBot):
    """Run trading bot in separate thread"""
    try:
        bot.start()
    except Exception as e:
        logger.error(f"Trading bot crashed: {e}", exc_info=True)


def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("GOLDMINE ML LIVE TRADING SYSTEM")
    logger.info("="*60)
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed. Check your .env file")
        sys.exit(1)
    
    logger.info(f"Configuration loaded:")
    logger.info(f"  API: {config.API_HOST}:{config.API_PORT}")
    logger.info(f"  Database: {config.DATABASE_URL[:30]}...")
    logger.info(f"  Model: {config.MODEL_PATH}")
    logger.info(f"  Max Daily Loss: ${config.MAX_DAILY_LOSS}")
    logger.info(f"  Min Confidence: {config.MIN_CONFIDENCE}")
    
    # Initialize trading bot
    logger.info("\nInitializing trading bot...")
    bot = LiveTradingBot()
    bot.set_websocket_manager(ws_manager)
    
    # Initialize API with bot instances
    logger.info("Initializing API...")
    init_api(bot, bot.terminal_manager, bot.db)
    
    # Add WebSocket endpoint to FastAPI app
    @app.websocket("/ws")
    async def websocket_route(websocket: WebSocket):
        await websocket_endpoint(websocket)
    
    # Start trading bot in background thread
    logger.info("Starting trading bot thread...")
    bot_thread = threading.Thread(target=run_trading_bot, args=(bot,), daemon=True)
    bot_thread.start()
    
    # Start API server
    logger.info(f"\nStarting API server on {config.API_HOST}:{config.API_PORT}...")
    logger.info(f"API Docs: http://localhost:{config.API_PORT}/docs")
    logger.info(f"WebSocket: ws://localhost:{config.API_PORT}/ws")
    logger.info("\n" + "="*60)
    logger.info("SYSTEM READY - Waiting for connections...")
    logger.info("="*60 + "\n")
    
    try:
        uvicorn.run(
            app,
            host=config.API_HOST,
            port=config.API_PORT,
            log_level="info",
            access_log=False
        )
    except KeyboardInterrupt:
        logger.info("\nShutdown signal received...")
        bot.stop()
        logger.info("System stopped")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        bot.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
