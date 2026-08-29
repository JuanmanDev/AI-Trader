# Alpaca Trading Integration

This guide explains how to use the Alpaca Trading API integration in AI-Trader.

## Overview

AI-Trader now supports real trading through [Alpaca Markets](https://alpaca.markets/), a commission-free trading API. The integration provides:

- ✅ Real-time market data
- ✅ Paper trading (simulation with real market data)
- ✅ Live trading capabilities
- ✅ Account and position management
- ✅ Order execution and tracking

## Setup

### 1. Get Alpaca API Credentials

1. Sign up for a free account at [Alpaca Markets](https://alpaca.markets/)
2. Navigate to your account settings
3. Generate API keys (you'll get an API Key and Secret Key)
4. Choose between Paper Trading or Live Trading

### 2. Configure Environment Variables

Add your Alpaca credentials to your `.env` file:

```bash
# Alpaca Trading API Configuration
ALPACA_API_KEY="your_api_key_here"
ALPACA_SECRET_KEY="your_secret_key_here"
ALPACA_BASE_URL="https://paper-api.alpaca.markets"  # For paper trading

# For live trading (use with caution!):
# ALPACA_BASE_URL="https://api.alpaca.markets"
```

### 3. Install Dependencies

The Alpaca SDK is included in the requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Paper Trading (Recommended for Testing)

Paper trading uses real market data but simulated money. This is perfect for testing strategies without risk.

1. Set up your `.env` file with paper trading URL (already default)
2. Start the Alpaca trading service:

```bash
cd agent_tools
python tool_alpaca_trade.py
```

The service will start on port 8004 by default.

### Live Trading (Use with Caution)

⚠️ **WARNING**: Live trading uses real money. Only use this if you understand the risks!

1. Change your `.env` to use the live trading URL:
```bash
ALPACA_BASE_URL="https://api.alpaca.markets"
```

2. Follow the same steps as paper trading

## Features

### Available Tools

The Alpaca integration provides several MCP tools:

1. **alpaca_buy(symbol, amount)** - Buy stocks
2. **alpaca_sell(symbol, amount)** - Sell stocks
3. **alpaca_get_account()** - Get account information
4. **alpaca_get_positions()** - Get current positions
5. **alpaca_get_price(symbol)** - Get current stock price

### Using Alpaca Data Provider

You can also use Alpaca for real-time market data in your custom scripts:

```python
from tools.alpaca_tools import AlpacaDataProvider

# Initialize data provider
data_provider = AlpacaDataProvider()

# Get latest price
price = data_provider.get_latest_price("AAPL")
print(f"AAPL current price: ${price}")

# Get historical data
bars = data_provider.get_historical_bars(
    symbol="AAPL",
    start_date="2024-01-01",
    end_date="2024-01-31",
    timeframe="1Day"
)
```

### Using Alpaca Trading Connector

For direct trading operations:

```python
from tools.alpaca_tools import AlpacaTradingConnector

# Initialize connector (paper trading by default)
connector = AlpacaTradingConnector(paper=True)

# Get account info
account = connector.get_account()
print(f"Buying power: ${account['buying_power']}")

# Buy stock
order = connector.buy_stock("AAPL", 10)
print(f"Order ID: {order['id']}")

# Check positions
positions = connector.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['qty']} shares @ ${pos['current_price']}")
```

## Integration with Existing System

### Option 1: Use Alpaca for Data Only

Keep using simulated trading but get real-time data from Alpaca:

1. Start Alpaca data service
2. Update your agent configuration to use Alpaca data source
3. Continue using the standard `tool_trade.py` for simulated trading

### Option 2: Full Alpaca Trading

Use Alpaca for both data and trading:

1. Configure your agent to use the Alpaca trading MCP service
2. Update MCP configuration in your agent to include Alpaca tools
3. The AI agent will use real trading through Alpaca

Example MCP configuration update:

```python
mcp_config = {
    "math": {"transport": "streamable_http", "url": "http://localhost:8000/mcp"},
    "stock_local": {"transport": "streamable_http", "url": "http://localhost:8003/mcp"},
    "search": {"transport": "streamable_http", "url": "http://localhost:8001/mcp"},
    "alpaca_trade": {"transport": "streamable_http", "url": "http://localhost:8004/mcp"},  # NEW
}
```

## Safety Features

- **Paper Trading by Default**: All examples use paper trading to prevent accidental real trades
- **Buying Power Checks**: Validates available funds before executing trades
- **Position Verification**: Checks position existence and quantity before selling
- **Error Handling**: Comprehensive error messages for debugging

## Troubleshooting

### "Alpaca SDK not installed"

Install the Alpaca SDK:
```bash
pip install alpaca-py
```

### "Alpaca API credentials not found"

Make sure your `.env` file has:
- `ALPACA_API_KEY`
- `ALPACA_SECRET_KEY`

### Connection Errors

1. Verify your API keys are correct
2. Check if you're using the right base URL (paper vs live)
3. Ensure your Alpaca account is active

### Rate Limits

Alpaca has rate limits on API calls:
- 200 requests per minute for most endpoints
- Consider implementing delays if you're making many rapid calls

## Best Practices

1. **Start with Paper Trading**: Always test strategies with paper trading first
2. **Monitor Your Positions**: Regularly check your account and positions
3. **Set Appropriate Limits**: Define max trade sizes and risk limits
4. **Keep API Keys Secure**: Never commit `.env` files to version control
5. **Log Everything**: Monitor AI decisions and trades carefully
6. **Test Thoroughly**: Run backtests before live trading

## Resources

- [Alpaca Documentation](https://alpaca.markets/docs/)
- [Alpaca Python SDK](https://github.com/alpacahq/alpaca-py)
- [Alpaca Community Forum](https://forum.alpaca.markets/)

## Limitations

- Only supports US stock trading (no crypto, forex, or options)
- Market hours restrictions apply
- Pattern day trader rules may apply
- Some stocks may not be available for trading

## Disclaimer

⚠️ **Trading Disclaimer**: Trading stocks involves risk. Past performance does not guarantee future results. This integration is provided as-is without any warranty. Use at your own risk. The developers are not responsible for any financial losses.
