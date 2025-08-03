#!/usr/bin/env python3
"""
Interactive Brokers MCP Server using FastMCP
Connects to IBKR API and executes trading operations
"""
import threading
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from decimal import Decimal

from fastmcp import FastMCP
from pydantic import BaseModel

# IBKR API imports (you'll need to install ibapi)
try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order
    from ibapi.ticktype import TickTypeEnum
    from ibapi.common import BarData
    import ibapi.wrapper
except ImportError:
    print("Warning: ibapi not installed. Install with: pip install ibapi")
    EClient = EWrapper = Contract = Order = TickTypeEnum = BarData = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastMCP server instance
mcp = FastMCP("IBKR Trading Server")

class IBKRConnection(EWrapper, EClient):
    """IBKR API connection handler"""
    
    def __init__(self):
        EClient.__init__(self, self)
        self.nextOrderId = None
        self.positions = {}
        self.account_info = {}
        self.market_data = {}
        self.orders = {}
        self.historical_data = {}
        self.connected = False
        self.data_received = threading.Event()
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        logger.error(f"Error {errorCode}: {errorString}")
        # Don't treat market data warnings as connection failures
        if errorCode in [2104, 2106, 2158, 10089]:  # Connection OK messages
            logger.info(f"Info {errorCode}: {errorString}")
        
    def nextValidId(self, orderId: int):
        """Receives the next valid order ID"""
        self.nextOrderId = orderId
        self.connected = True  # Set connected here when we get valid order ID
        logger.info(f"Connected! Next valid order ID: {orderId}")
        
    def connectAck(self):
        """Confirms connection to TWS/Gateway"""
        logger.info("Connection acknowledged by IBKR")
        
    def connectionClosed(self):
        """Connection closed"""
        self.connected = False
        logger.info("Connection to IBKR closed")
        
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        """Receives position data"""
        key = f"{contract.symbol}-{contract.secType}-{contract.exchange}"
        self.positions[key] = {
            'account': account,
            'symbol': contract.symbol,
            'secType': contract.secType,
            'exchange': contract.exchange,
            'position': position,
            'avgCost': avgCost,
            'marketValue': position * avgCost
        }
        
    def positionEnd(self):
        """Position data complete"""
        logger.info("Position data received")
        self.data_received.set()
        
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        """Receives account summary data"""
        self.account_info[tag] = {
            'value': value,
            'currency': currency
        }
        
    def accountSummaryEnd(self, reqId: int):
        """Account summary complete"""
        logger.info("Account summary received")
        self.data_received.set()
        
    def tickPrice(self, reqId: int, tickType, price: float, attrib):
        """Receives market data price ticks"""
        if reqId not in self.market_data:
            self.market_data[reqId] = {}
        self.market_data[reqId][TickTypeEnum.to_str(tickType)] = price
        
    def orderStatus(self, orderId: int, status: str, filled: float, remaining: float, 
                   avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, 
                   clientId: int, whyHeld: str, mktCapPrice: float):
        """Receives order status updates"""
        self.orders[orderId] = {
            'orderId': orderId,
            'status': status,
            'filled': filled,
            'remaining': remaining,
            'avgFillPrice': avgFillPrice,
            'lastFillPrice': lastFillPrice
        }
        
    def openOrder(self, orderId: int, contract: Contract, order: Order, orderState):
        """Receives open order details"""
        self.orders[orderId] = {
            'orderId': orderId,
            'symbol': contract.symbol,
            'secType': contract.secType,
            'exchange': contract.exchange,
            'action': order.action,
            'orderType': order.orderType,
            'totalQuantity': order.totalQuantity,
            'lmtPrice': getattr(order, 'lmtPrice', None),
            'auxPrice': getattr(order, 'auxPrice', None),
            'status': getattr(orderState, 'status', 'Unknown'),
            'contract': contract,
            'order': order
        }
        
    def openOrderEnd(self):
        """Open orders request complete"""
        logger.info("Open orders data received")
        self.data_received.set()
        
    def historicalData(self, reqId, bar: BarData):
        """Receive historical data bars"""
        if reqId not in self.historical_data:
            self.historical_data[reqId] = []
            
        self.historical_data[reqId].append({
            'date': bar.date,
            'open': bar.open,
            'high': bar.high, 
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        })
        
    def historicalDataEnd(self, reqId, start, end):
        """Historical data request completed"""
        logger.info(f"Historical data received for request {reqId}")
        self.data_received.set()

# Global IBKR connection
ibkr_client = None
connection_lock = threading.Lock()

async def get_ibkr_connection():
    """Get or create IBKR connection"""
    global ibkr_client
    
    with connection_lock:
        if ibkr_client is None or not ibkr_client.connected:
            logger.info("Creating new IBKR connection...")
            ibkr_client = IBKRConnection()
            
            # Try to connect to IB Gateway first (port 4001), then TWS (port 7497)
            connected = False
            
            for port, name in [(4001, "IB Gateway"), (7497, "TWS Paper Trading")]:
                try:
                    logger.info(f"Attempting to connect to {name} on port {port}...")
                    ibkr_client.connect("127.0.0.1", port, 0)
                    
                    # Start the socket in a separate thread
                    api_thread = threading.Thread(target=ibkr_client.run, daemon=True)
                    api_thread.start()
                    
                    # Wait for connection with longer timeout
                    timeout = 30  # 30 seconds timeout
                    start_time = time.time()
                    
                    while not ibkr_client.connected and (time.time() - start_time) < timeout:
                        await asyncio.sleep(0.1)
                        
                    if ibkr_client.connected:
                        logger.info(f"Successfully connected to {name}")
                        connected = True
                        break
                    else:
                        logger.warning(f"Failed to connect to {name}")
                        ibkr_client.disconnect()
                        
                except Exception as e:
                    logger.error(f"Error connecting to {name}: {e}")
                    
            if not connected:
                raise ConnectionError("Failed to connect to IBKR. Make sure TWS or IB Gateway is running and API connections are enabled.")
                
    return ibkr_client

@mcp.tool()
async def get_open_orders() -> Dict[str, Any]:
    """Get all open/pending orders"""
    try:
        client = await get_ibkr_connection()
        
        # Clear previous data
        client.orders.clear()
        client.data_received.clear()
        
        # Request open orders
        client.reqOpenOrders()
        
        # Wait for data
        client.data_received.wait(timeout=10)
        
        return {
            "open_orders": client.orders,
            "total_open_orders": len(client.orders),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_all_orders() -> Dict[str, Any]:
    """Get all orders (completed and pending)"""
    try:
        client = await get_ibkr_connection()
        
        # Clear previous data
        client.orders.clear()
        client.data_received.clear()
        
        # Request all orders
        client.reqAllOpenOrders()
        
        # Wait for data
        client.data_received.wait(timeout=10)
        
        return {
            "all_orders": client.orders,
            "total_orders": len(client.orders),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_connection_status() -> Dict[str, Any]:
    """Check IBKR connection status"""
    global ibkr_client
    
    if ibkr_client is None:
        return {
            "connected": False, 
            "message": "No connection attempted",
            "recommendation": "Make sure TWS or IB Gateway is running"
        }
    
    return {
        "connected": ibkr_client.connected,
        "next_order_id": ibkr_client.nextOrderId,
        "positions_count": len(ibkr_client.positions),
        "account_info_fields": list(ibkr_client.account_info.keys()),
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
async def connect_to_ibkr() -> Dict[str, Any]:
    """Manually trigger connection to IBKR"""
    try:
        client = await get_ibkr_connection()
        return {
            "success": True,
            "connected": client.connected,
            "next_order_id": client.nextOrderId,
            "message": "Successfully connected to IBKR"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to connect to IBKR"
        }

@mcp.tool()
async def get_account_summary() -> Dict[str, Any]:
    """Get account summary including buying power, cash, etc."""
    try:
        client = await get_ibkr_connection()
        
        # Clear previous data
        client.account_info.clear()
        client.data_received.clear()
        
        # Request account summary
        tags = "TotalCashValue,NetLiquidation,GrossPositionValue,AvailableFunds"
        client.reqAccountSummary(9001, "All", tags)
        
        # Wait for data
        client.data_received.wait(timeout=10)
        
        return {
            "account_info": client.account_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_positions() -> Dict[str, Any]:
    """Get all current positions"""
    try:
        client = await get_ibkr_connection()
        
        # Clear previous data
        client.positions.clear()
        client.data_received.clear()
        
        # Request positions
        client.reqPositions()
        
        # Wait for data
        client.data_received.wait(timeout=10)
        
        return {
            "positions": client.positions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_market_data(symbol: str, exchange: str = "SMART", sec_type: str = "STK") -> Dict[str, Any]:
    """Get real-time market data for a symbol"""
    try:
        client = await get_ibkr_connection()
        
        # Create contract
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = "USD"
        
        # Request market data
        req_id = 1001
        client.reqMktData(req_id, contract, "", False, False, [])
        
        # Wait for data
        await asyncio.sleep(3)
        
        # Cancel the data request to avoid accumulating subscriptions
        client.cancelMktData(req_id)
        
        return {
            "symbol": symbol,
            "market_data": client.market_data.get(req_id, {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def place_order(
    symbol: str,
    action: str,  # BUY or SELL
    quantity: int,
    order_type: str = "MKT",  # MKT, LMT, STP, etc.
    limit_price: Optional[float] = None,
    exchange: str = "SMART",
    sec_type: str = "STK"
) -> Dict[str, Any]:
    """Place a trading order"""
    try:
        client = await get_ibkr_connection()
        
        if client.nextOrderId is None:
            return {"error": "No valid order ID available"}
        
        # Create contract
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = "USD"
        
        # Create order
        order = Order()
        order.action = action.upper()
        order.totalQuantity = quantity
        order.orderType = order_type.upper()
        
        if order_type.upper() == "LMT" and limit_price:
            order.lmtPrice = limit_price
            
        # Place order
        order_id = client.nextOrderId
        client.placeOrder(order_id, contract, order)
        client.nextOrderId += 1
        
        # Wait for order confirmation
        await asyncio.sleep(1)
        
        return {
            "order_id": order_id,
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "order_type": order_type,
            "limit_price": limit_price,
            "status": "submitted",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def cancel_order(order_id: int) -> Dict[str, Any]:
    """Cancel an existing order"""
    try:
        client = await get_ibkr_connection()
        
        client.cancelOrder(order_id, "")
        
        return {
            "order_id": order_id,
            "status": "cancel_requested",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_order_status(order_id: int) -> Dict[str, Any]:
    """Get status of a specific order"""
    try:
        client = await get_ibkr_connection()
        
        order_info = client.orders.get(order_id, {})
        
        return {
            "order_id": order_id,
            "order_info": order_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_historical_data(
    symbol: str,
    duration: str = "1 D",  # 1 D, 1 W, 1 M, etc.
    bar_size: str = "1 min",  # 1 min, 5 mins, 1 hour, 1 day, etc.
    what_to_show: str = "TRADES",  # TRADES, MIDPOINT, BID, ASK
    exchange: str = "SMART",
    sec_type: str = "STK"
) -> Dict[str, Any]:
    """Get historical market data"""
    try:
        client = await get_ibkr_connection()
        
        # Create contract
        contract = Contract()
        contract.symbol = symbol.upper()
        contract.secType = sec_type
        contract.exchange = exchange
        contract.currency = "USD"
        
        # Request historical data
        req_id = 2001
        end_datetime = ""  # Empty string means current time
        
        # Clear previous data
        if req_id in client.historical_data:
            del client.historical_data[req_id]
        client.data_received.clear()
        
        client.reqHistoricalData(
            req_id, contract, end_datetime, duration, bar_size, 
            what_to_show, 1, 1, False, []
        )
        
        # Wait for data
        client.data_received.wait(timeout=15)
        
        historical_bars = client.historical_data.get(req_id, [])
        
        return {
            "symbol": symbol,
            "duration": duration,
            "bar_size": bar_size,
            "bars_count": len(historical_bars),
            "historical_data": historical_bars,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def calculate_portfolio_metrics() -> Dict[str, Any]:
    """Calculate portfolio metrics like total value, P&L, etc."""
    try:
        client = await get_ibkr_connection()
        
        # Clear previous data
        client.positions.clear()
        client.account_info.clear()
        
        # Get fresh data
        client.data_received.clear()
        client.reqPositions()
        client.data_received.wait(timeout=10)
        
        client.data_received.clear()
        tags = "TotalCashValue,NetLiquidation,GrossPositionValue,AvailableFunds"
        client.reqAccountSummary(9002, "All", tags)
        client.data_received.wait(timeout=10)
        
        total_market_value = sum(
            pos.get('marketValue', 0) for pos in client.positions.values()
        )
        
        cash = float(client.account_info.get('TotalCashValue', {}).get('value', 0))
        net_liquidation = float(client.account_info.get('NetLiquidation', {}).get('value', 0))
        
        return {
            "total_positions": len(client.positions),
            "total_market_value": total_market_value,
            "cash_balance": cash,
            "net_liquidation_value": net_liquidation,
            "buying_power": float(client.account_info.get('AvailableFunds', {}).get('value', 0)),
            "positions": client.positions,
            "account_summary": client.account_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()