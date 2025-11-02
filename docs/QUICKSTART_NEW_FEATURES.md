# Quick Start Guide for New Features

This guide helps you get started with the new Alpaca Trading and multi-LLM features.

## Option 1: Use Ollama (Free Local LLM)

Perfect for testing without API costs!

### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:** Download from [ollama.ai](https://ollama.ai/)

### Step 2: Pull a Model

```bash
# Start Ollama
ollama serve

# In another terminal, pull a model
ollama pull llama2
# or
ollama pull mistral
```

### Step 3: Configure AI-Trader

Use the example config:
```bash
cp configs/example_ollama_config.json configs/my_config.json
```

Edit `configs/my_config.json` and enable the Ollama model:
```json
{
  "name": "llama2-local",
  "basemodel": "ollama/llama2",
  "signature": "llama2-local",
  "enabled": true
}
```

### Step 4: Run

```bash
# Make sure Ollama is running in another terminal
ollama serve

# Run AI-Trader
python main.py configs/my_config.json
```

## Option 2: Use Alpaca Paper Trading

Trade with real market data but simulated money!

### Step 1: Get Alpaca API Keys

1. Sign up at [alpaca.markets](https://alpaca.markets/)
2. Get your API keys from the dashboard

### Step 2: Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your Alpaca keys:
```bash
ALPACA_API_KEY="your_api_key"
ALPACA_SECRET_KEY="your_secret_key"
ALPACA_BASE_URL="https://paper-api.alpaca.markets"
```

### Step 3: Start Alpaca Trading Service

```bash
cd agent_tools
python tool_alpaca_trade.py
```

This starts the Alpaca MCP service on port 8004.

### Step 4: Configure Your Agent

Update your agent's MCP configuration to include Alpaca:

```python
mcp_config = {
    "math": {"transport": "streamable_http", "url": "http://localhost:8000/mcp"},
    "stock_local": {"transport": "streamable_http", "url": "http://localhost:8003/mcp"},
    "search": {"transport": "streamable_http", "url": "http://localhost:8001/mcp"},
    "trade": {"transport": "streamable_http", "url": "http://localhost:8002/mcp"},
    "alpaca_trade": {"transport": "streamable_http", "url": "http://localhost:8004/mcp"},
}
```

## Option 3: Use Both!

Run local LLMs with Alpaca paper trading:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start MCP services
cd agent_tools
python start_mcp_services.py

# Terminal 3: Start Alpaca service
cd agent_tools
python tool_alpaca_trade.py

# Terminal 4: Run AI-Trader with Ollama
python main.py configs/example_ollama_config.json
```

## Testing the Setup

### Test Ollama

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test with Python
python -c "from tools.llm_factory import LLMFactory; llm = LLMFactory.create_llm('ollama/llama2'); print('Ollama OK!')"
```

### Test Alpaca

```bash
# Test connection
python -c "from tools.alpaca_tools import AlpacaDataProvider; dp = AlpacaDataProvider(); print('Alpaca OK!')"
```

## Common Issues

### Ollama: "Connection refused"

Make sure Ollama is running:
```bash
ollama serve
```

### Alpaca: "API credentials not found"

Check your `.env` file has:
- ALPACA_API_KEY
- ALPACA_SECRET_KEY

### Dependencies Missing

Install all requirements:
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Read the Documentation**
   - [Alpaca Integration Guide](ALPACA_INTEGRATION.md)
   - [LLM Providers Guide](LLM_PROVIDERS.md)

2. **Try Different Models**
   - Compare GPT-4 vs local models
   - Test different Ollama models (mistral, mixtral, phi)

3. **Experiment with Strategies**
   - Use paper trading to test safely
   - Compare model performance
   - Adjust parameters

## Cost Comparison

| Option | Cost | Speed | Quality |
|--------|------|-------|---------|
| GPT-4 | $$$ | Medium | Excellent |
| GPT-3.5 | $ | Fast | Good |
| Ollama (Llama 2) | Free | Fast* | Good |
| Ollama (Mistral) | Free | Fast* | Good |
| Ollama (Mixtral) | Free | Medium* | Very Good |

*Speed depends on your hardware (GPU recommended)

## Support

- Issues: [GitHub Issues](https://github.com/JuanmanDev/AI-Trader/issues)
- Discussions: [GitHub Discussions](https://github.com/JuanmanDev/AI-Trader/discussions)
