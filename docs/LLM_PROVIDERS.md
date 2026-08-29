# LLM Provider Support

This guide explains how to use different LLM providers with AI-Trader, including OpenAI, Ollama, Anthropic, and others.

## Overview

AI-Trader now supports multiple LLM providers through a flexible LLM factory system. You can use:

- ✅ **OpenAI** (GPT-4, GPT-3.5, etc.)
- ✅ **Ollama** (Local LLMs like Llama 2, Mistral, etc.)
- ✅ **Anthropic** (Claude models)
- ✅ **Any OpenAI-compatible API** (via base URL configuration)

## Quick Start

### Using OpenAI (Default)

```json
{
  "models": [
    {
      "name": "gpt-4",
      "basemodel": "openai/gpt-4",
      "signature": "gpt-4",
      "enabled": true
    }
  ]
}
```

Environment variables:
```bash
OPENAI_API_KEY="your_openai_api_key"
OPENAI_API_BASE="https://api.openai.com/v1"  # Optional
```

### Using Ollama (Local LLMs)

```json
{
  "models": [
    {
      "name": "llama2-local",
      "basemodel": "ollama/llama2",
      "signature": "llama2-local",
      "enabled": true
    }
  ]
}
```

Environment variables:
```bash
OLLAMA_BASE_URL="http://localhost:11434"
```

### Using Anthropic Claude

```json
{
  "models": [
    {
      "name": "claude-3-opus",
      "basemodel": "anthropic/claude-3-opus-20240229",
      "signature": "claude-3-opus",
      "enabled": true
    }
  ]
}
```

Environment variables:
```bash
ANTHROPIC_API_KEY="your_anthropic_api_key"
```

## Provider-Specific Guides

### Ollama Setup

[Ollama](https://ollama.ai/) allows you to run LLMs locally on your machine.

#### 1. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/)

#### 2. Pull a Model

```bash
# Pull Llama 2 (7B)
ollama pull llama2

# Pull Mistral (7B)
ollama pull mistral

# Pull Mixtral (8x7B)
ollama pull mixtral

# Pull smaller models for faster inference
ollama pull phi
ollama pull gemma
```

#### 3. Start Ollama Server

```bash
ollama serve
```

The server runs on `http://localhost:11434` by default.

#### 4. Configure AI-Trader

Add to `configs/default_config.json`:

```json
{
  "models": [
    {
      "name": "llama2-7b",
      "basemodel": "ollama/llama2",
      "signature": "llama2-7b",
      "enabled": true
    },
    {
      "name": "mistral-7b",
      "basemodel": "ollama/mistral",
      "signature": "mistral-7b",
      "enabled": true
    }
  ]
}
```

#### 5. Run Trading

```bash
python main.py configs/default_config.json
```

### OpenAI-Compatible APIs

Many services offer OpenAI-compatible APIs. You can use them by setting the base URL:

#### Using OpenRouter

```json
{
  "models": [
    {
      "name": "claude-via-openrouter",
      "basemodel": "anthropic/claude-3-opus",
      "signature": "claude-openrouter",
      "enabled": true,
      "openai_base_url": "https://openrouter.ai/api/v1",
      "openai_api_key": "your_openrouter_key"
    }
  ]
}
```

#### Using Together AI

```json
{
  "models": [
    {
      "name": "mixtral-together",
      "basemodel": "mistralai/Mixtral-8x7B-Instruct-v0.1",
      "signature": "mixtral-together",
      "enabled": true,
      "openai_base_url": "https://api.together.xyz/v1",
      "openai_api_key": "your_together_key"
    }
  ]
}
```

## Configuration Reference

### Model Configuration Schema

```json
{
  "name": "human-readable-name",
  "basemodel": "provider/model-name",
  "signature": "unique-identifier",
  "enabled": true,
  "provider": "optional-explicit-provider",
  "openai_base_url": "optional-api-url",
  "openai_api_key": "optional-api-key",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

### Field Descriptions

- **name**: Display name for the model
- **basemodel**: Model identifier with optional provider prefix
  - Format: `provider/model-name` or just `model-name`
  - Examples: `openai/gpt-4`, `ollama/llama2`, `gpt-4`
- **signature**: Unique ID used for data storage (must be unique)
- **enabled**: Whether to run this model
- **provider**: Explicit provider (optional, auto-detected from basemodel)
  - Options: `openai`, `ollama`, `anthropic`
- **openai_base_url**: Custom API endpoint (optional)
- **openai_api_key**: Model-specific API key (optional)
- **temperature**: Sampling temperature (0.0 to 2.0)
- **max_tokens**: Maximum response length

### Provider Auto-Detection

The system automatically detects the provider from the model name:

| Model Name Pattern | Detected Provider |
|-------------------|-------------------|
| `gpt-4`, `gpt-3.5`, `o1-*` | OpenAI |
| `llama*`, `mistral*`, `phi*`, `gemma*` | Ollama |
| `claude*`, `anthropic/*` | Anthropic |

You can override auto-detection by adding an explicit provider prefix:
- `openai/custom-model`
- `ollama/custom-model`

## Advanced Usage

### Running Multiple Models Simultaneously

```json
{
  "models": [
    {
      "name": "gpt-4-trader",
      "basemodel": "openai/gpt-4",
      "signature": "gpt-4-trader",
      "enabled": true
    },
    {
      "name": "llama2-trader",
      "basemodel": "ollama/llama2",
      "signature": "llama2-trader",
      "enabled": true
    },
    {
      "name": "mistral-trader",
      "basemodel": "ollama/mistral",
      "signature": "mistral-trader",
      "enabled": true
    }
  ]
}
```

All enabled models will trade simultaneously in the same market conditions.

### Custom Model Parameters

```json
{
  "name": "creative-gpt4",
  "basemodel": "openai/gpt-4",
  "signature": "creative-gpt4",
  "enabled": true,
  "temperature": 1.2,
  "max_tokens": 8192
}
```

### Using Local and Cloud Models Together

```json
{
  "models": [
    {
      "name": "gpt4-premium",
      "basemodel": "openai/gpt-4",
      "signature": "gpt4",
      "enabled": true
    },
    {
      "name": "llama2-local",
      "basemodel": "ollama/llama2",
      "signature": "llama2",
      "enabled": true
    }
  ]
}
```

## Performance Considerations

### Ollama Models

- **Speed**: Local models are faster (no network latency)
- **Cost**: Free to run locally
- **Quality**: May vary; smaller models (7B) are less capable than GPT-4
- **Resources**: Requires good GPU for acceptable performance

Recommended models for trading:
- `mixtral:8x7b` - Best quality for local use
- `mistral:7b` - Good balance of speed and quality
- `llama2:13b` - Higher quality, slower
- `phi:2.7b` - Very fast, lower quality

### Cloud APIs

- **Speed**: Network latency (typically 1-3 seconds)
- **Cost**: Pay per token
- **Quality**: Generally higher quality (especially GPT-4, Claude)
- **Resources**: No local requirements

## Troubleshooting

### Ollama Issues

**Model not found:**
```bash
ollama pull <model-name>
```

**Connection refused:**
```bash
# Make sure Ollama is running
ollama serve
```

**Slow inference:**
- Use smaller models (7B instead of 13B/70B)
- Ensure GPU is available
- Check system resources

### OpenAI Issues

**Invalid API key:**
- Check `OPENAI_API_KEY` in `.env`
- Verify key is active in OpenAI dashboard

**Rate limit errors:**
- Add delays between requests
- Use lower-tier models (gpt-3.5-turbo)

### General Issues

**Import errors:**
```bash
pip install -r requirements.txt
```

**Provider not detected:**
- Add explicit provider prefix: `ollama/model-name`
- Or set `"provider": "ollama"` in config

## Best Practices

1. **Test Locally First**: Use Ollama to test strategies without API costs
2. **Monitor Costs**: Track API usage when using cloud providers
3. **Choose Appropriate Models**: 
   - Complex strategies → GPT-4, Claude
   - Simple strategies → GPT-3.5, Mistral
   - High-frequency → Local Ollama models
4. **Benchmark Performance**: Compare different models on same data
5. **Use Paper Trading**: Test all models with paper trading first

## Supported Models Examples

### OpenAI
- `gpt-4`, `gpt-4-turbo`
- `gpt-3.5-turbo`
- `o1-preview`, `o1-mini`

### Ollama
- `llama2`, `llama2:13b`, `llama2:70b`
- `mistral`, `mistral:7b`
- `mixtral`, `mixtral:8x7b`
- `phi`, `phi:2.7b`
- `gemma`, `gemma:7b`
- `codellama`, `codellama:13b`

### Anthropic
- `claude-3-opus-20240229`
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

## Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.ai/library)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [LangChain Docs](https://python.langchain.com/)

## Contributing

To add support for a new LLM provider:

1. Install the provider's LangChain integration
2. Add provider detection logic to `tools/llm_factory.py`
3. Implement provider-specific initialization
4. Update documentation
5. Submit a pull request

Example provider addition:

```python
# In tools/llm_factory.py
@staticmethod
def _create_custom_provider(model_name, **kwargs):
    from langchain_custom import ChatCustom
    return ChatCustom(model=model_name, **kwargs)
```
