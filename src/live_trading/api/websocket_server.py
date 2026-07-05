"""
WebSocket server for real-time updates to frontend
"""
import logging
import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
import socketio

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections and broadcasts"""
    
    def __init__(self):
        """Initialize WebSocket manager"""
        self.active_connections: Set[WebSocket] = set()
        self.logger = logging.getLogger(__name__)
        self.logger.info("WebSocket manager initialized")
    
    async def connect(self, websocket: WebSocket):
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        self.logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "message": "Connected to Goldmine ML Trading",
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.discard(websocket)
        self.logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send message to specific client
        
        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            self.logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients
        
        Args:
            message: Message dictionary to broadcast
        """
        if not self.active_connections:
            return
        
        # Add timestamp if not present
        if 'timestamp' not in message:
            message['timestamp'] = datetime.now().isoformat()
        
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                self.logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    # ===== EVENT EMITTERS =====
    
    async def emit_new_signal(self, signal_data: Dict):
        """
        Emit new signal event
        
        Args:
            signal_data: Signal information
        """
        await self.broadcast({
            "type": "new_signal",
            "data": signal_data
        })
        self.logger.info(f"Broadcasted new signal: {signal_data.get('signal')}")
    
    async def emit_trade_opened(self, trade_data: Dict):
        """
        Emit trade opened event
        
        Args:
            trade_data: Trade information
        """
        await self.broadcast({
            "type": "trade_opened",
            "data": trade_data
        })
        self.logger.info(f"Broadcasted trade opened: {trade_data.get('ticket')}")
    
    async def emit_trade_closed(self, trade_data: Dict):
        """
        Emit trade closed event
        
        Args:
            trade_data: Trade close information
        """
        await self.broadcast({
            "type": "trade_closed",
            "data": trade_data
        })
        self.logger.info(f"Broadcasted trade closed: {trade_data.get('ticket')}")
    
    async def emit_position_update(self, position_data: Dict):
        """
        Emit position update (floating P&L)
        
        Args:
            position_data: Position information
        """
        await self.broadcast({
            "type": "position_update",
            "data": position_data
        })
    
    async def emit_account_update(self, account_data: Dict):
        """
        Emit account information update
        
        Args:
            account_data: Account information
        """
        await self.broadcast({
            "type": "account_update",
            "data": account_data
        })
    
    async def emit_metrics_update(self, metrics_data: Dict):
        """
        Emit performance metrics update
        
        Args:
            metrics_data: Metrics information
        """
        await self.broadcast({
            "type": "metrics_update",
            "data": metrics_data
        })
    
    async def emit_connection_status(self, status_data: Dict):
        """
        Emit connection status change
        
        Args:
            status_data: Connection status
        """
        await self.broadcast({
            "type": "connection_status",
            "data": status_data
        })
        self.logger.info(f"Broadcasted connection status: {status_data.get('connected')}")
    
    async def emit_error(self, error_data: Dict):
        """
        Emit error event
        
        Args:
            error_data: Error information
        """
        await self.broadcast({
            "type": "error",
            "data": error_data
        })
        self.logger.warning(f"Broadcasted error: {error_data.get('message')}")
    
    async def emit_daily_summary(self, summary_data: Dict):
        """
        Emit daily summary update
        
        Args:
            summary_data: Daily summary
        """
        await self.broadcast({
            "type": "daily_summary",
            "data": summary_data
        })
    
    async def emit_system_status(self, status_data: Dict):
        """
        Emit system status update
        
        Args:
            status_data: System status
        """
        await self.broadcast({
            "type": "system_status",
            "data": status_data
        })
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global WebSocket manager instance
ws_manager = WebSocketManager()


# FastAPI WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication
    
    Args:
        websocket: WebSocket connection
    """
    await ws_manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle client messages
                msg_type = message.get('type')
                
                if msg_type == 'ping':
                    await ws_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                elif msg_type == 'subscribe':
                    # Handle subscription to specific events
                    await ws_manager.send_personal_message({
                        "type": "subscribed",
                        "events": message.get('events', [])
                    }, websocket)
                
                else:
                    logger.warning(f"Unknown message type: {msg_type}")
            
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# Utility functions for background tasks

async def periodic_account_update(bot, interval: int = 5):
    """
    Periodically broadcast account updates
    
    Args:
        bot: Trading bot instance
        interval: Update interval in seconds
    """
    while True:
        try:
            if bot.mt5.check_connection():
                account_info = bot.mt5.get_account_info()
                if account_info:
                    await ws_manager.emit_account_update(account_info)
        except Exception as e:
            logger.error(f"Error in periodic account update: {e}")
        
        await asyncio.sleep(interval)


async def periodic_position_update(bot, interval: int = 1):
    """
    Periodically broadcast position updates
    
    Args:
        bot: Trading bot instance
        interval: Update interval in seconds
    """
    while True:
        try:
            if bot.executor:
                positions = bot.executor.get_open_positions()
                for position in positions:
                    await ws_manager.emit_position_update(position)
        except Exception as e:
            logger.error(f"Error in periodic position update: {e}")
        
        await asyncio.sleep(interval)


async def periodic_metrics_update(bot, db_manager, interval: int = 60):
    """
    Periodically broadcast metrics updates
    
    Args:
        bot: Trading bot instance
        db_manager: Database manager instance
        interval: Update interval in seconds
    """
    while True:
        try:
            # Calculate current metrics
            trades = db_manager.get_trade_history(limit=1000)
            
            if trades:
                winning = [t for t in trades if t.profit > 0]
                losing = [t for t in trades if t.profit < 0]
                
                metrics = {
                    "total_trades": len(trades),
                    "winning_trades": len(winning),
                    "losing_trades": len(losing),
                    "win_rate": (len(winning) / len(trades)) * 100 if trades else 0,
                    "net_profit": sum(t.profit for t in trades),
                }
                
                await ws_manager.emit_metrics_update(metrics)
        except Exception as e:
            logger.error(f"Error in periodic metrics update: {e}")
        
        await asyncio.sleep(interval)
