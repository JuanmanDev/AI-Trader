"""
Alpaca Trading API Integration Module

This module provides integration with Alpaca Markets for:
1. Real-time and historical market data
2. Real trading execution
3. Account and position management
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
    from alpaca.data.timeframe import TimeFrame
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️  Alpaca SDK not installed. Install with: pip install alpaca-py")


class AlpacaDataProvider:
    """
    Alpaca data provider for real-time and historical market data
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize Alpaca data provider
        
        Args:
            api_key: Alpaca API key (defaults to env var ALPACA_API_KEY)
            secret_key: Alpaca secret key (defaults to env var ALPACA_SECRET_KEY)
            base_url: Alpaca base URL (defaults to env var ALPACA_BASE_URL or paper trading)
        """
        if not ALPACA_AVAILABLE:
            raise ImportError("Alpaca SDK is not installed. Install with: pip install alpaca-py")
        
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.base_url = base_url or os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY")
        
        # Initialize data client (doesn't require base_url)
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)
        
        print(f"✅ Alpaca data provider initialized (using {self.base_url})")
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get latest price for a symbol
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            
        Returns:
            Latest price as float, or None if not available
        """
        try:
            request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.data_client.get_stock_latest_quote(request_params)
            
            if symbol in quotes:
                quote = quotes[symbol]
                # Use mid price between bid and ask
                return (quote.bid_price + quote.ask_price) / 2.0
            return None
        except Exception as e:
            print(f"❌ Error getting latest price for {symbol}: {e}")
            return None
    
    def get_historical_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        timeframe: str = "1Day"
    ) -> List[Dict[str, Any]]:
        """
        Get historical price bars for a symbol
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today
            timeframe: Bar timeframe ("1Day", "1Hour", etc.)
            
        Returns:
            List of bar data dictionaries
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Map timeframe string to TimeFrame enum
            timeframe_map = {
                "1Day": TimeFrame.Day,
                "1Hour": TimeFrame.Hour,
                "1Min": TimeFrame.Minute,
            }
            tf = timeframe_map.get(timeframe, TimeFrame.Day)
            
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=datetime.strptime(start_date, "%Y-%m-%d"),
                end=datetime.strptime(end_date, "%Y-%m-%d")
            )
            
            bars = self.data_client.get_stock_bars(request_params)
            
            result = []
            if symbol in bars:
                for bar in bars[symbol]:
                    result.append({
                        "timestamp": bar.timestamp.isoformat(),
                        "open": float(bar.open),
                        "high": float(bar.high),
                        "low": float(bar.low),
                        "close": float(bar.close),
                        "volume": int(bar.volume)
                    })
            
            return result
        except Exception as e:
            print(f"❌ Error getting historical bars for {symbol}: {e}")
            return []


class AlpacaTradingConnector:
    """
    Alpaca trading connector for real trading execution
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
        paper: bool = True
    ):
        """
        Initialize Alpaca trading connector
        
        Args:
            api_key: Alpaca API key (defaults to env var ALPACA_API_KEY)
            secret_key: Alpaca secret key (defaults to env var ALPACA_SECRET_KEY)
            base_url: Alpaca base URL (defaults to env var ALPACA_BASE_URL)
            paper: Whether to use paper trading (default: True)
        """
        if not ALPACA_AVAILABLE:
            raise ImportError("Alpaca SDK is not installed. Install with: pip install alpaca-py")
        
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        
        # Determine base URL
        if base_url:
            self.base_url = base_url
        elif paper:
            self.base_url = "https://paper-api.alpaca.markets"
        else:
            self.base_url = os.getenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY")
        
        # Initialize trading client
        self.trading_client = TradingClient(
            self.api_key,
            self.secret_key,
            paper=paper,
            url_override=self.base_url if not paper else None
        )
        
        self.paper = paper
        trading_type = "PAPER" if paper else "LIVE"
        print(f"✅ Alpaca trading connector initialized ({trading_type} trading at {self.base_url})")
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information
        
        Returns:
            Dictionary with account information
        """
        try:
            account = self.trading_client.get_account()
            return {
                "account_number": account.account_number,
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "buying_power": float(account.buying_power),
                "equity": float(account.equity),
                "status": account.status,
            }
        except Exception as e:
            print(f"❌ Error getting account info: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get all current positions
        
        Returns:
            List of position dictionaries
        """
        try:
            positions = self.trading_client.get_all_positions()
            result = []
            for pos in positions:
                result.append({
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "market_value": float(pos.market_value),
                    "cost_basis": float(pos.cost_basis),
                    "unrealized_pl": float(pos.unrealized_pl),
                    "current_price": float(pos.current_price),
                })
            return result
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return []
    
    def buy_stock(self, symbol: str, qty: int, order_type: str = "market") -> Dict[str, Any]:
        """
        Buy stock
        
        Args:
            symbol: Stock symbol
            qty: Quantity to buy
            order_type: Order type ("market" or "limit")
            
        Returns:
            Order confirmation dictionary
        """
        try:
            if order_type == "market":
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            order = self.trading_client.submit_order(order_data)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            }
        except Exception as e:
            print(f"❌ Error buying {symbol}: {e}")
            return {"error": str(e)}
    
    def sell_stock(self, symbol: str, qty: int, order_type: str = "market") -> Dict[str, Any]:
        """
        Sell stock
        
        Args:
            symbol: Stock symbol
            qty: Quantity to sell
            order_type: Order type ("market" or "limit")
            
        Returns:
            Order confirmation dictionary
        """
        try:
            if order_type == "market":
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
            else:
                raise ValueError(f"Unsupported order type: {order_type}")
            
            order = self.trading_client.submit_order(order_data)
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            }
        except Exception as e:
            print(f"❌ Error selling {symbol}: {e}")
            return {"error": str(e)}
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        try:
            order = self.trading_client.get_order_by_id(order_id)
            return {
                "id": order.id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "status": order.status.value,
                "side": order.side.value,
            }
        except Exception as e:
            print(f"❌ Error getting order status: {e}")
            return {"error": str(e)}


def is_alpaca_enabled() -> bool:
    """Check if Alpaca integration is enabled and configured"""
    return (
        ALPACA_AVAILABLE and
        os.getenv("ALPACA_API_KEY") is not None and
        os.getenv("ALPACA_SECRET_KEY") is not None
    )
