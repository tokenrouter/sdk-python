# TokenRouter Python SDK

[![PyPI version](https://badge.fury.io/py/tokenrouter.svg)](https://badge.fury.io/py/tokenrouter)
[![Python Versions](https://img.shields.io/pypi/pyversions/tokenrouter.svg)](https://pypi.org/project/tokenrouter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-tokenrouter.io-blue)](https://docs.tokenrouter.io)

Official Python SDK for [TokenRouter](https://tokenrouter.io) - an intelligent LLM routing service that automatically selects the most cost-effective model for your AI requests while maintaining quality.

## 🚀 Why TokenRouter?

TokenRouter is a unified gateway that intelligently routes your LLM requests to the most suitable provider and model based on your specific needs. Instead of managing multiple API keys, handling different response formats, and manually optimizing costs, TokenRouter handles it all for you.

### Key Benefits
- **70% Cost Reduction**: Automatically routes to cheaper models for simple tasks
- **100% OpenAI Compatible**: Drop-in replacement for existing OpenAI code
- **6+ LLM Providers**: Access OpenAI, Anthropic, Google, Mistral, Meta, and more through one API
- **Automatic Fallbacks**: Seamlessly switches providers during outages
- **Built-in Analytics**: Track costs, latency, and usage across all providers

## ✨ Features

- 🚀 **OpenAI-Compatible Interface**: Drop-in replacement for OpenAI SDK
- 🎯 **Intelligent Routing**: Automatically selects optimal model based on task complexity
- 💰 **Cost Optimization**: Reduce LLM costs by up to 70% automatically
- 🔄 **Multi-Provider Support**: OpenAI, Anthropic, Google, Mistral, Meta Llama, Deepseek
- ⚡ **Streaming Support**: Real-time streaming responses with proper error handling
- 🔒 **Enterprise Security**: Compliant with encrypted API key storage
- 🔁 **Automatic Retries**: Built-in exponential backoff and provider failover
- 📊 **Detailed Analytics**: Track usage, costs, and performance metrics
- 🔀 **Async Support**: Both synchronous and asynchronous clients
- 🔑 **Provider Support**: Bring Your Own Keys for complete control

## 📦 Installation

### Requirements
- Python 3.7 or higher
- pip package manager

### Install from PyPI

```bash
pip install tokenrouter
```

### Install from Source

```bash
git clone https://github.com/tokenrouter/tokenrouter-python.git
cd tokenrouter-python
pip install -e .
```

### Install with Optional Dependencies

```bash
# With development tools
pip install tokenrouter[dev]

# With async support optimizations
pip install tokenrouter[async]
```

## Quick Start

### Basic Usage

```python
from tokenrouter import TokenRouter

# Initialize client
client = TokenRouter(
    api_key="tr_your-api-key-here",
    base_url="https://api.tokenrouter.io"
)

# Simple completion
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="auto",  # Let TokenRouter choose the best model
    mode="balanced",  # Routing strategy: 'cost', 'quality', 'latency', or 'balanced'
    temperature=0.7
)

print(response.content)
print(f"Cost: ${response.cost_usd:.6f}")
print(f"Model used: {response.model}")
```

### Async Usage

```python
import asyncio
from tokenrouter import AsyncTokenRouter

async def main():
    # Initialize async client
    client = AsyncTokenRouter(
        api_key="tr_your-api-key-here",
        base_url="https://api.tokenrouter.io"
    )
    
    # Async completion
    response = await client.chat.create(
        messages=[
            {"role": "user", "content": "Explain quantum computing"}
        ],
        model="auto",
        max_tokens=500
    )
    
    print(response.content)
    
    # Don't forget to close the client
    await client.close()

asyncio.run(main())
```

## Authentication

Get your API key from TokenRouter:

1. Sign up at [tokenrouter.io](https://tokenrouter.io)
2. Navigate to API Keys section
3. Create a new API key
4. Add to your environment:

```bash
export TOKENROUTER_API_KEY=tr_your-api-key-here
```

Then in your code:
```python
import os
from tokenrouter import TokenRouter

client = TokenRouter(api_key=os.environ["TOKENROUTER_API_KEY"])
```

## Core Features

### Automatic Model Selection

Let TokenRouter choose the best model for your use case:

```python
# TokenRouter analyzes your prompt and selects the optimal model
response = client.chat.create(
    messages=[{"role": "user", "content": "Write a haiku about coding"}],
    model="auto"  # Automatic selection
)
```

### Model Preferences

Specify preferred models while still benefiting from fallback:

```python
response = client.chat.create(
    messages=[{"role": "user", "content": "Explain relativity"}],
    model_preferences=["gpt-4", "claude-3-opus"],  # Preference order
    max_tokens=1000
)
```

### Streaming Responses

Stream responses for real-time output:

```python
# Synchronous streaming
stream = client.chat.create(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="auto",
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Async streaming
async def stream_response():
    stream = await async_client.chat.create(
        messages=[{"role": "user", "content": "Count to 10"}],
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
```

### Function Calling / Tools

Use OpenAI-compatible function calling:

```python
response = client.chat.create(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    model="auto",
    tools=[{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }],
    tool_choice="auto"
)

# Handle tool calls in response
if response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"Function: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
```

### Direct Completions

Simple completion interface:

```python
# Quick completion
response = client.completions("Translate 'Hello' to French")
print(response.content)

# With parameters
response = client.completions(
    "Write a Python function for binary search",
    model="auto",
    temperature=0.2,
    max_tokens=500
)
```

## Advanced Usage

### Custom Headers

Add custom headers to requests:

```python
client = TokenRouter(
    api_key="tr_your-api-key",
    headers={
        "X-Custom-Header": "value"
    }
)
```

### Timeout Configuration

Set custom timeout values:

```python
client = TokenRouter(
    api_key="tr_your-api-key",
    timeout=30.0  # 30 seconds
)
```

### Error Handling

Comprehensive error handling:

```python
from tokenrouter import (
    TokenRouter,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError
)

try:
    response = client.chat.create(
        messages=[{"role": "user", "content": "Hello"}],
        model="auto"
    )
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded, retry after: {e.retry_after}")
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
except APIConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Analytics & Monitoring

Track usage and costs:

```python
# Get usage analytics
analytics = client.get_analytics()
print(f"Total requests: {analytics.total_requests}")
print(f"Total cost: ${analytics.total_cost_usd:.4f}")
print(f"Average latency: {analytics.average_latency_ms}ms")

# List available models
models = client.list_models()
for model in models:
    print(f"{model.id}: {model.provider}")

# Get model costs
costs = client.get_costs()
for model, pricing in costs.items():
    print(f"{model}: ${pricing['cost_per_1k_input']}/1k input tokens")
```

## API Methods

### Chat Completions

```python
client.chat.create(
    messages,           # List of message dicts (required)
    model="auto",       # Model name or 'auto'
    model_preferences=None,  # List of preferred models
    temperature=0.7,    # Sampling temperature (0-2)
    max_tokens=None,    # Maximum tokens to generate
    top_p=1.0,         # Nucleus sampling parameter
    frequency_penalty=0.0,  # Frequency penalty (-2 to 2)
    presence_penalty=0.0,   # Presence penalty (-2 to 2)
    stop=None,         # Stop sequences
    stream=False,      # Enable streaming
    tools=None,        # Function/tool definitions
    tool_choice=None,  # Tool selection strategy
    response_format=None,  # Response format spec
    seed=None,         # Seed for deterministic output
    user=None          # User identifier for tracking
)
```

### Direct Completions

```python
client.completions(
    prompt,            # Prompt string (required)
    model="auto",      # Model name or 'auto'
    **kwargs           # Additional parameters
)
```

### Utility Methods

```python
# List available models
models = client.list_models()

# Get model pricing
costs = client.get_costs()

# Get usage analytics
analytics = client.get_analytics()

# Health check
health = client.health_check()
```

## Environment Variables

```bash
# Required
TOKENROUTER_API_KEY=tr_your-api-key

# Optional
TOKENROUTER_BASE_URL=https://api.tokenrouter.io
TOKENROUTER_TIMEOUT=30
TOKENROUTER_MAX_RETRIES=3
```

## Migration from OpenAI

TokenRouter SDK is designed as a drop-in replacement for OpenAI:

```python
# Before (OpenAI)
import openai
openai.api_key = "sk-..."
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)

# After (TokenRouter)
from tokenrouter import TokenRouter
client = TokenRouter(api_key="tr_...")
response = client.chat.create(
    model="auto",  # or keep "gpt-3.5-turbo"
    messages=[{"role": "user", "content": "Hello"}]
)
```

## 🏆 Best Practices

### 1. Model Selection
```python
# ✅ Good: Let TokenRouter optimize
response = client.chat.create(
    model="auto",  # Intelligent routing
    messages=[...]
)

# ⚠️ Avoid: Hardcoding expensive models unnecessarily
response = client.chat.create(
    model="gpt-4",  # May be overkill for simple tasks
    messages=[...]
)
```

### 2. Error Handling
```python
# ✅ Good: Comprehensive error handling
import time
from tokenrouter import TokenRouter, RateLimitError

def safe_completion(client, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.create(messages=messages, model="auto")
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(e.retry_after or (2 ** attempt))
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

### 3. Cost Optimization
- **Use streaming** for long responses to improve UX
- **Set appropriate max_tokens** to avoid unnecessary generation
- **Cache responses** for repeated queries
- **Monitor usage** regularly through analytics

### 4. Performance Tips
- Use **AsyncTokenRouter** for concurrent requests
- Implement **connection pooling** (handled automatically)
- Set **reasonable timeouts** based on your use case
- Use **model preferences** for critical requests
- Enable **response caching** for common queries

## Examples

### Example: Content Generation

```python
def generate_blog_post(topic: str) -> str:
    response = client.chat.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional blog writer"
            },
            {
                "role": "user",
                "content": f"Write a 500-word blog post about {topic}"
            }
        ],
        model="auto",
        temperature=0.8,
        max_tokens=1000
    )
    return response.content
```

### Example: Code Generation

```python
def generate_code(description: str) -> str:
    response = client.chat.create(
        messages=[
            {
                "role": "system",
                "content": "You are an expert programmer. Return only code without explanations."
            },
            {
                "role": "user",
                "content": description
            }
        ],
        model="auto",
        temperature=0.2,  # Lower temperature for code
        max_tokens=2000
    )
    return response.content
```

### Example: Batch Processing

```python
async def process_batch(prompts: list) -> list:
    async with AsyncTokenRouter(api_key="tr_...") as client:
        tasks = []
        for prompt in prompts:
            task = client.chat.create(
                messages=[{"role": "user", "content": prompt}],
                model="auto"
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [r.content for r in responses]

# Usage
prompts = ["Question 1", "Question 2", "Question 3"]
results = asyncio.run(process_batch(prompts))
```

### Example: Conversation with Context

```python
class Conversation:
    def __init__(self, client, system_prompt=None):
        self.client = client
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
    
    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})
    
    def get_response(self, **kwargs):
        response = self.client.chat.create(
            messages=self.messages,
            model="auto",
            **kwargs
        )
        self.messages.append({"role": "assistant", "content": response.content})
        return response.content

# Usage
conv = Conversation(TokenRouter, "You are a helpful tutor")
conv.add_user_message("What is calculus?")
response1 = conv.get_response()
conv.add_user_message("Can you give an example?")
response2 = conv.get_response()  # Has context of previous messages
```

## Error Reference

| Exception | Description | Resolution |
|-----------|-------------|------------|
| `AuthenticationError` | Invalid or missing API key | Check API key validity |
| `RateLimitError` | Rate limit exceeded | Wait and retry with backoff |
| `InvalidRequestError` | Malformed request | Check request parameters |
| `APIConnectionError` | Network error | Check network connection |
| `InternalServerError` | Server error | Retry with exponential backoff |

## Performance Tips

1. **Use connection pooling**: The client reuses connections automatically
2. **Batch requests**: Process multiple prompts concurrently with AsyncClient
3. **Set appropriate timeouts**: Balance between reliability and speed
4. **Cache frequently used responses**: Implement local caching for common queries
5. **Monitor token usage**: Track token consumption to optimize prompts

## 🤖 Supported Models

TokenRouter supports models from all major providers:

For a full list of supported models visit https://tokenrouter.io/leaderboard/ 

## 🔧 Advanced Configuration

### Environment Variables

```bash
# API Configuration
TOKENROUTER_API_KEY=tr_your-api-key        # Your TokenRouter API key
TOKENROUTER_BASE_URL=https://api.tokenrouter.io  # API endpoint
TOKENROUTER_TIMEOUT=30                     # Request timeout in seconds
TOKENROUTER_MAX_RETRIES=3                  # Maximum retry attempts
```

### Custom Client Configuration

```python
from tokenrouter import TokenRouter

client = TokenRouter(
    api_key="tr_your-api-key",
    base_url="https://api.tokenrouter.io",
    timeout=30.0,
    max_retries=3,
    headers={
        "X-Custom-Header": "value"
    },
)
```

## 🔒 Security

- **API Keys**: All API keys are encrypted at rest using AES-256
- **Transport**: All API calls use HTTPS with TLS 1.2+
- **Compliance**: SOC2 Type II compliant
- **Data Privacy**: No training on user data
- **Key Rotation**: Support for automatic key rotation
- **Audit Logs**: Complete audit trail of all API usage

## 📊 Monitoring & Analytics

### Built-in Analytics

```python
# Get detailed usage analytics
analytics = client.get_analytics(
    start_date="2024-01-01",
    end_date="2024-01-31"
)

print(f"Total Requests: {analytics.total_requests}")
print(f"Total Cost: ${analytics.total_cost_usd:.2f}")
print(f"Average Latency: {analytics.avg_latency_ms}ms")
print(f"Cost Savings: ${analytics.savings_usd:.2f}")

# Model-specific metrics
for model in analytics.models:
    print(f"{model.name}: {model.requests} requests, ${model.cost:.2f}")
```

### Real-time Monitoring

```python
# Monitor individual request metrics
response = client.chat.create(
    messages=[{"role": "user", "content": "Hello"}],
    model="auto",
    metadata={"user_id": "user123", "session": "abc"}  # Custom tracking
)

print(f"Request ID: {response.request_id}")
print(f"Latency: {response.latency_ms}ms")
print(f"Cost: ${response.cost_usd:.6f}")
print(f"Model Used: {response.model}")
print(f"Provider: {response.provider}")
```

## 🚀 Performance Benchmarks

| Operation | TokenRouter | Direct API | Improvement |
|-----------|------------|------------|-------------|
| Simple Query | 250ms | 400ms | 37.5% faster |
| Complex Query | 1.2s | 1.8s | 33% faster |
| With Caching | 50ms | 400ms | 87.5% faster |
| Cost per 1K requests | $8.50 | $28.00 | 70% cheaper |

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial stable release
- Full OpenAI compatibility
- Support for 6 major LLM providers
- Streaming support
- Async client
- BYOK mode
- Comprehensive error handling
- Analytics and monitoring

### Roadmap
- [ ] Local key config
- [ ] Custom rules
- [ ] WebSocket support for real-time streaming
- [ ] Batch API for bulk processing
- [ ] Fine-tuning support
- [ ] Prompt caching and optimization
- [ ] Multi-region support
- [ ] GraphQL API support


```bash
# Clone the repository
git clone https://github.com/tokenrouter/tokenrouter-python.git
cd tokenrouter-python

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Format code
black tokenrouter/
isort tokenrouter/

# Type checking
mypy tokenrouter/
```

## 📞 Support

- **Documentation**: [docs.tokenrouter.io](https://docs.tokenrouter.io)
- **API Reference**: [docs.tokenrouter.io/api](https://docs.tokenrouter.io/api)
- **GitHub Issues**: [github.com/tokenrouter/tokenrouter-python/issues](https://github.com/tokenrouter/tokenrouter-python/issues)
- **Discord Community**: [discord.gg/tokenrouter](https://discord.gg/tokenrouter)
- **Email Support**: support@tokenrouter.io
- **Enterprise Support**: enterprise@tokenrouter.io

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by the TokenRouter Team<br>
  <a href="https://tokenrouter.io">tokenrouter.io</a> • 
  <a href="https://docs.tokenrouter.io">Documentation</a> • 
  <a href="https://github.com/tokenrouter">GitHub</a>
</p>