"""
Alpaca-enabled Trading Tool

This MCP tool provides trading functionality using Alpaca's API for real trading.
It can be used as an alternative to the simulated trading in tool_trade.py
"""

from fastmcp import FastMCP
import sys
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.general_tools import get_config_value, write_config_value
from tools.alpaca_tools import AlpacaTradingConnector, AlpacaDataProvider, is_alpaca_enabled
import json

mcp = FastMCP("AlpacaTradeTools")

# Global connectors (initialized on first use)
_trading_connector: Optional[AlpacaTradingConnector] = None
_data_provider: Optional[AlpacaDataProvider] = None


def _get_trading_connector() -> AlpacaTradingConnector:
    """Get or create Alpaca trading connector"""
    global _trading_connector
    if _trading_connector is None:
        _trading_connector = AlpacaTradingConnector(paper=True)
    return _trading_connector


def _get_data_provider() -> AlpacaDataProvider:
    """Get or create Alpaca data provider"""
    global _data_provider
    if _data_provider is None:
        _data_provider = AlpacaDataProvider()
    return _data_provider


@mcp.tool()
def alpaca_buy(symbol: str, amount: int) -> Dict[str, Any]:
    """
    Buy stock using Alpaca Trading API
    
    This function executes real stock purchases through Alpaca Markets.
    It uses paper trading by default for safety.
    
    Args:
        symbol: Stock symbol, such as "AAPL", "MSFT", etc.
        amount: Buy quantity, must be a positive integer
        
    Returns:
        Dict[str, Any]:
          - Success: Returns order confirmation with order ID and details
          - Failure: Returns {"error": error message} dictionary
        
    Example:
        >>> result = alpaca_buy("AAPL", 10)
        >>> print(result)  # {"id": "...", "symbol": "AAPL", "qty": 10, ...}
    """
    if not is_alpaca_enabled():
        return {
            "error": "Alpaca integration not enabled. Please configure ALPACA_API_KEY and ALPACA_SECRET_KEY",
            "symbol": symbol,
            "amount": amount
        }
    
    try:
        connector = _get_trading_connector()
        
        # Get current account to check buying power
        account = connector.get_account()
        
        # Get current price to estimate cost
        data_provider = _get_data_provider()
        price = data_provider.get_latest_price(symbol)
        
        if price is None:
            return {
                "error": f"Unable to get price for {symbol}",
                "symbol": symbol
            }
        
        estimated_cost = price * amount
        buying_power = account.get("buying_power", 0)
        
        if estimated_cost > buying_power:
            return {
                "error": "Insufficient buying power",
                "required": estimated_cost,
                "available": buying_power,
                "symbol": symbol
            }
        
        # Execute buy order
        result = connector.buy_stock(symbol, amount)
        
        if "error" not in result:
            write_config_value("IF_TRADE", True)
            print(f"✅ Alpaca BUY order submitted: {symbol} x {amount}")
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to execute buy order: {str(e)}",
            "symbol": symbol,
            "amount": amount
        }


@mcp.tool()
def alpaca_sell(symbol: str, amount: int) -> Dict[str, Any]:
    """
    Sell stock using Alpaca Trading API
    
    This function executes real stock sales through Alpaca Markets.
    It uses paper trading by default for safety.
    
    Args:
        symbol: Stock symbol, such as "AAPL", "MSFT", etc.
        amount: Sell quantity, must be a positive integer
        
    Returns:
        Dict[str, Any]:
          - Success: Returns order confirmation with order ID and details
          - Failure: Returns {"error": error message} dictionary
        
    Example:
        >>> result = alpaca_sell("AAPL", 10)
        >>> print(result)  # {"id": "...", "symbol": "AAPL", "qty": 10, ...}
    """
    if not is_alpaca_enabled():
        return {
            "error": "Alpaca integration not enabled. Please configure ALPACA_API_KEY and ALPACA_SECRET_KEY",
            "symbol": symbol,
            "amount": amount
        }
    
    try:
        connector = _get_trading_connector()
        
        # Check current positions
        positions = connector.get_positions()
        position = next((p for p in positions if p["symbol"] == symbol), None)
        
        if position is None:
            return {
                "error": f"No position found for {symbol}",
                "symbol": symbol
            }
        
        if position["qty"] < amount:
            return {
                "error": "Insufficient shares to sell",
                "have": position["qty"],
                "want_to_sell": amount,
                "symbol": symbol
            }
        
        # Execute sell order
        result = connector.sell_stock(symbol, amount)
        
        if "error" not in result:
            write_config_value("IF_TRADE", True)
            print(f"✅ Alpaca SELL order submitted: {symbol} x {amount}")
        
        return result
        
    except Exception as e:
        return {
            "error": f"Failed to execute sell order: {str(e)}",
            "symbol": symbol,
            "amount": amount
        }


@mcp.tool()
def alpaca_get_account() -> Dict[str, Any]:
    """
    Get Alpaca account information
    
    Returns current account status including cash, portfolio value, and buying power.
    
    Returns:
        Dict with account information or error
    """
    if not is_alpaca_enabled():
        return {"error": "Alpaca integration not enabled"}
    
    try:
        connector = _get_trading_connector()
        return connector.get_account()
    except Exception as e:
        return {"error": f"Failed to get account info: {str(e)}"}


@mcp.tool()
def alpaca_get_positions() -> Dict[str, Any]:
    """
    Get all current positions in Alpaca account
    
    Returns list of all open positions with current values.
    
    Returns:
        Dict with positions list or error
    """
    if not is_alpaca_enabled():
        return {"error": "Alpaca integration not enabled"}
    
    try:
        connector = _get_trading_connector()
        positions = connector.get_positions()
        return {"positions": positions, "count": len(positions)}
    except Exception as e:
        return {"error": f"Failed to get positions: {str(e)}"}


@mcp.tool()
def alpaca_get_price(symbol: str) -> Dict[str, Any]:
    """
    Get current price for a stock symbol
    
    Args:
        symbol: Stock symbol (e.g., "AAPL")
        
    Returns:
        Dict with price information or error
    """
    if not is_alpaca_enabled():
        return {"error": "Alpaca integration not enabled"}
    
    try:
        data_provider = _get_data_provider()
        price = data_provider.get_latest_price(symbol)
        
        if price is None:
            return {"error": f"Unable to get price for {symbol}"}
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": "latest"
        }
    except Exception as e:
        return {"error": f"Failed to get price: {str(e)}"}


if __name__ == "__main__":
    port = int(os.getenv("ALPACA_TRADE_HTTP_PORT", "8004"))
    
    if is_alpaca_enabled():
        print(f"🚀 Starting Alpaca Trading MCP service on port {port}")
        mcp.run(transport="streamable-http", port=port)
    else:
        print("❌ Alpaca integration not enabled. Please configure:")
        print("   - ALPACA_API_KEY")
        print("   - ALPACA_SECRET_KEY")
        print("   in your .env file")
