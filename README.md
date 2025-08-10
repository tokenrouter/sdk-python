# TokenRouter Python SDK

Official Python SDK for TokenRouter - an intelligent LLM routing service that automatically selects the most cost-effective model for your AI requests.

## Features

- 🚀 **OpenAI-Compatible Interface**: Drop-in replacement for OpenAI SDK
- 🎯 **Intelligent Routing**: Automatically routes to the best model based on your prompt
- 💰 **Cost Optimization**: Save up to 70% on LLM costs
- 🔄 **Multiple Providers**: Unified interface for OpenAI, Anthropic, Mistral, Together AI
- ⚡ **Streaming Support**: Real-time streaming responses  
- 🔒 **Built-in Authentication**: Secure API key management
- 🔁 **Automatic Retries**: Resilient error handling
- 📊 **Analytics**: Track usage, costs, and performance
- 🔀 **Async Support**: Both synchronous and asynchronous clients

## Installation

```bash
pip install tokenrouter
```

For development/local testing:
```bash
cd TokenRouterSDK/python
pip install -e .
```

## Quick Start

### Basic Usage

```python
from tokenrouter import Client

# Initialize client
client = Client(
    api_key="tr_your-api-key-here",
    base_url="https://api.tokenrouter.io"  # or http://localhost:8000 for local
)

# Simple completion
response = client.chat.create(
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ],
    model="auto",  # Let TokenRouter choose the best model
    temperature=0.7
)

print(response.content)
print(f"Cost: ${response.cost_usd:.6f}")
print(f"Model used: {response.model}")
```

### Async Usage

```python
import asyncio
from tokenrouter import AsyncClient

async def main():
    # Initialize async client
    client = AsyncClient(
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
from tokenrouter import Client

client = Client(api_key=os.environ["TOKENROUTER_API_KEY"])
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
client = Client(
    api_key="tr_your-api-key",
    headers={
        "X-Custom-Header": "value"
    }
)
```

### Timeout Configuration

Set custom timeout values:

```python
client = Client(
    api_key="tr_your-api-key",
    timeout=30.0  # 30 seconds
)
```

### Error Handling

Comprehensive error handling:

```python
from tokenrouter import (
    Client,
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
from tokenrouter import Client
client = Client(api_key="tr_...")
response = client.chat.create(
    model="auto",  # or keep "gpt-3.5-turbo"
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Best Practices

1. **Use 'auto' model**: Let TokenRouter optimize model selection
2. **Implement retries**: Use exponential backoff for transient errors
3. **Cache responses**: Store frequently requested completions
4. **Batch similar requests**: Group related prompts when possible
5. **Monitor costs**: Regularly check analytics to track spending
6. **Use async client**: For concurrent requests, use AsyncClient
7. **Close connections**: Always close async clients when done

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
    async with AsyncClient(api_key="tr_...") as client:
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
conv = Conversation(client, "You are a helpful tutor")
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

## Support

- **Documentation**: [docs.tokenrouter.io](https://docs.tokenrouter.io)
- **GitHub Issues**: [github.com/tokenrouter/sdk-python/issues](https://github.com/tokenrouter/sdk-python/issues)
- **Email**: support@tokenrouter.io
- **Discord**: [discord.gg/tokenrouter](https://discord.gg/tokenrouter)

## License

MIT License - see [LICENSE](LICENSE) file for details.