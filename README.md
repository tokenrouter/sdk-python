# TokenRouter Python SDK

OpenAI Responses API compatible client for TokenRouter - intelligent LLM routing service.

## Installation

```bash
pip install tokenrouter
```

## Quick Start

```python
import tokenrouter

client = tokenrouter.TokenRouter(
    api_key=os.environ['TOKENROUTER_API_KEY'],  # This is the default and can be omitted
    base_url=os.environ.get('TOKENROUTER_BASE_URL', 'https://api.tokenrouter.io/api'),  # Default
)

response = client.responses.create({
    "model": "gpt-4.1",
    "input": "Tell me a three sentence bedtime story about a unicorn."
})

print(response.output_text)
```

## OpenAI Compatibility

This SDK is designed to be a drop-in replacement for OpenAI's SDK when using the Responses API. Simply change your import and API key:

```python
# Before (OpenAI)
from openai import OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# After (TokenRouter)
import tokenrouter
client = tokenrouter.TokenRouter(api_key=os.environ["TOKENROUTER_API_KEY"])
```

## API Reference

### Create Response

```python
response = client.responses.create({
    # Required
    "input": "Your prompt here",  # or list of input items

    # Optional
    "model": "gpt-4.1",  # Model to use
    "instructions": "System instructions",
    "max_output_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "stream": False,  # Set to True for streaming
    "tools": [],  # Function calling tools
    "tool_choice": "auto",
    "text": {"format": {"type": "text"}},  # Response format
    # ... other OpenAI-compatible parameters
})

# Access the response text directly
print(response.output_text)
```

### Streaming Responses

```python
stream = client.responses.create({
    "input": "Write a poem",
    "stream": True
})

for event in stream:
    if event.type == 'response.delta' and event.delta and event.delta.output:
        for item in event.delta.output:
            if item.get("content"):
                for content in item["content"]:
                    if content.get("text"):
                        print(content["text"], end="")
```

### Function Calling

```python
response = client.responses.create({
    "input": "What's the weather in San Francisco?",
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
})

# Check for function calls in the response
for item in response.output:
    if item.get("type") == "tool_call" and item.get("tool_calls"):
        for tool_call in item["tool_calls"]:
            if tool_call.get("function"):
                print(f"Function: {tool_call['function']['name']}")
                print(f"Arguments: {tool_call['function']['arguments']}")
```

### Multi-turn Conversations

```python
# First message
response1 = client.responses.create({
    "input": "My name is Alice",
    "store": True  # Store for later retrieval
})

# Continue conversation
response2 = client.responses.create({
    "input": "What's my name?",
    "previous_response_id": response1.id
})
```

### Other Methods

```python
# Get response by ID
response = client.responses.get("resp_123")

# Delete response
result = client.responses.delete("resp_123")

# Cancel background response
response = client.responses.cancel("resp_123")

# List input items
items = client.responses.list_input_items("resp_123")
```

## Error Handling

```python
from tokenrouter import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError
)

try:
    response = client.responses.create({
        "input": "Hello"
    })
except AuthenticationError:
    print('Invalid API key')
except RateLimitError as e:
    print(f'Rate limit exceeded, retry after: {e.retry_after}')
except InvalidRequestError as e:
    print(f'Invalid request: {e.message}')
except TokenRouterError as e:
    print(f'Unexpected error: {e}')
```

## Configuration

### Environment Variables

```bash
export TOKENROUTER_API_KEY=tr_your-api-key
export TOKENROUTER_BASE_URL=https://api.tokenrouter.io/api  # Optional
```

### Client Options

```python
client = tokenrouter.TokenRouter(
    api_key='tr_...',  # Your API key
    base_url='https://api.tokenrouter.io/api',  # API base URL
    timeout=60.0,  # Request timeout in seconds (default: 60)
    max_retries=3,  # Max retry attempts (default: 3)
    headers={  # Additional headers
        'X-Custom-Header': 'value'
    }
)
```

## Type Support

The SDK provides type hints for better IDE support:

```python
from tokenrouter import TokenRouter, Response, ResponseStreamEvent
from tokenrouter.types import ResponsesCreateParams

params: ResponsesCreateParams = {
    "input": "Hello",
    "model": "gpt-4.1"
}

response: Response = client.responses.create(params)
```

## Examples

See the [examples](./examples) directory for more detailed usage examples:

- [simple.py](./examples/simple.py) - Basic usage
- [responses_example.py](./examples/responses_example.py) - Comprehensive examples

## License

MIT

### Client Options

```python
from tokenrouter import TokenRouter

client = TokenRouter(
    api_key='tr_...',  # Your API key
    base_url='https://api.tokenrouter.io/api',  # API base URL
    timeout=60.0,  # Request timeout in seconds (default: 60)
    max_retries=3,  # Max retry attempts (default: 3)
    headers={  # Additional headers
        'X-Custom-Header': 'value'
    }
)
```

## API Reference

### Create Response

```python
response = client.responses.create(
    # Required
    input="Your prompt here",  # or list of input items

    # Optional
    model="gpt-4.1",  # Model to use
    instructions="System instructions",
    max_output_tokens=1000,
    temperature=0.7,
    top_p=0.9,
    stream=False,  # Set to True for streaming
    tools=[],  # Function calling tools
    tool_choice="auto",
    text={"format": {"type": "text"}},  # Response format
    # ... other OpenAI-compatible parameters
)

# Access the response text directly
print(response.output_text)
```

### Streaming Responses

```python
stream = client.responses.create(
    input="Write a poem",
    stream=True
)

for event in stream:
    if event.type == "response.delta" and event.delta and event.delta.output:
        for item in event.delta.output:
            if item.get("content"):
                for content in item["content"]:
                    if content.get("text"):
                        print(content["text"], end="", flush=True)
```

### Function Calling

```python
response = client.responses.create(
    input="What's the weather in San Francisco?",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
)

# Check for function calls in the response
for item in response.output:
    if item.type == "tool_call" and item.tool_calls:
        for tool_call in item.tool_calls:
            if tool_call.function:
                print(f"Function: {tool_call.function.get('name')}")
                print(f"Arguments: {tool_call.function.get('arguments')}")
```

### Multi-turn Conversations

```python
# First message
response1 = client.responses.create(
    input="My name is Alice",
    store=True  # Store for later retrieval
)

# Continue conversation
response2 = client.responses.create(
    input="What's my name?",
    previous_response_id=response1.id
)
```

### Other Methods

```python
# Get response by ID
response = client.responses.get("resp_123")

# Delete response
result = client.responses.delete("resp_123")

# Cancel background response
response = client.responses.cancel("resp_123")

# List input items
items = client.responses.list_input_items("resp_123")
```

## Async Support

The SDK provides a fully async client for asynchronous applications:

```python
import asyncio
from tokenrouter import AsyncTokenRouter

async def main():
    async with AsyncTokenRouter(api_key="tr_...") as client:
        response = await client.responses.create(
            input="Hello, world!"
        )
        print(response.output_text)

asyncio.run(main())
```

### Async Streaming

```python
async with AsyncTokenRouter(api_key="tr_...") as client:
    stream = await client.responses.create(
        input="Count to 5",
        stream=True
    )

    async for event in stream:
        if event.type == "response.delta" and event.delta:
            # Process streaming chunks
            pass
```

## Response Format

The SDK adds a convenience property `output_text` to responses that aggregates all text output:

```python
response = client.responses.create(input="Hello")

# Access aggregated text directly
print(response.output_text)

# Or access the full response structure
print(response.output)  # List of output items
print(response.usage)  # Token usage
print(response.model)  # Model used
```

## Error Handling

```python
from tokenrouter import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError
)

try:
    response = client.responses.create(input="Hello")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit exceeded, retry after: {e.retry_after}")
except InvalidRequestError as e:
    print(f"Invalid request: {e.message}")
except TokenRouterError as e:
    print(f"Unexpected error: {e}")
```

## Type Hints

The SDK provides comprehensive type hints for all models:

```python
from tokenrouter import TokenRouter, Response, ResponseStreamEvent
from typing import Iterator

def process_response(response: Response) -> str:
    return response.output_text or ""

def handle_stream(stream: Iterator[ResponseStreamEvent]) -> None:
    for event in stream:
        # Process events with full type support
        pass
```

## Examples

See the [examples](./examples) directory for more detailed usage:

- [simple.py](./examples/simple.py) - Basic usage matching the OpenAI pattern
- [responses_example.py](./examples/responses_example.py) - Comprehensive examples of all features

## Requirements

- Python 3.7+
- httpx>=0.24.0
- typing-extensions>=4.0.0

## License

MIT