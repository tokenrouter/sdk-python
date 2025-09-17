"""
TokenRouter SDK - Comprehensive Responses API Examples
"""

import os
import json
import tokenrouter
from tokenrouter import TokenRouterError, RateLimitError

# Set your API key (or use environment variable TOKENROUTER_API_KEY)
api_key = os.environ.get("TOKENROUTER_API_KEY", "your-api-key")
base_url = os.environ.get("TOKENROUTER_BASE_URL", "https://api.tokenrouter.io/api")


def example_simple_response():
    """Example 1: Simple text generation"""
    print("Example 1: Simple text generation")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    response = client.responses.create({
        "model": "gpt-4.1",
        "input": "Tell me a three sentence bedtime story about a unicorn."
    })

    print(f"Response: {response.output_text}")
    print(f"Model used: {response.model}")
    print()


def example_with_instructions():
    """Example 2: With system instructions"""
    print("Example 2: With system instructions")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    response = client.responses.create({
        "model": "gpt-4.1",
        "instructions": "You are a helpful assistant that always responds in haiku format.",
        "input": "What is the meaning of life?"
    })

    print(f"Response: {response.output_text}")
    print()


def example_structured_input():
    """Example 3: Using structured input"""
    print("Example 3: Using structured input")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    response = client.responses.create({
        "model": "gpt-4.1",
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "What's the weather like today?"
                    }
                ]
            }
        ]
    })

    print(f"Response: {response.output_text}")
    print()


def example_streaming():
    """Example 4: Streaming responses"""
    print("Example 4: Streaming response")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    stream = client.responses.create({
        "model": "gpt-4.1",
        "input": "Write a short poem about coding",
        "stream": True
    })

    for event in stream:
        if event.type == "response.delta" and event.delta and event.delta.output:
            for item in event.delta.output:
                if item.get("content"):
                    for content in item["content"]:
                        if content.get("text"):
                            print(content["text"], end="", flush=True)

    print("\n")


def example_function_calling():
    """Example 5: Function calling"""
    print("Example 5: Function calling")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    response = client.responses.create({
        "model": "gpt-4.1",
        "input": "What's the weather in San Francisco?",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"]
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    })

    # Check if the model called a function
    for item in response.output:
        if item.get("type") == "tool_call" and item.get("tool_calls"):
            for tool_call in item["tool_calls"]:
                if tool_call.get("type") == "function" and tool_call.get("function"):
                    print(f"Function called: {tool_call['function'].get('name')}")
                    print(f"Arguments: {tool_call['function'].get('arguments')}")
    print()


def example_json_response():
    """Example 6: JSON response format"""
    print("Example 6: JSON response format")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    response = client.responses.create({
        "model": "gpt-4.1",
        "input": "List three benefits of exercise",
        "text": {
            "format": {
                "type": "json_object"
            }
        }
    })

    print(f"Response: {response.output_text}")

    # Try to parse as JSON
    try:
        json_response = json.loads(response.output_text)
        print(f"Parsed JSON: {json.dumps(json_response, indent=2)}")
    except json.JSONDecodeError:
        print("(Response was not valid JSON)")
    print()


def example_temperature_control():
    """Example 7: Temperature and sampling control"""
    print("Example 7: Temperature control")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    response = client.responses.create({
        "model": "gpt-4.1",
        "input": "Generate a creative name for a coffee shop",
        "temperature": 0.9,
        "top_p": 0.95,
        "max_output_tokens": 50
    })

    print(f"Response: {response.output_text}")
    print()


def example_conversation_state():
    """Example 8: Multi-turn conversation"""
    print("Example 8: Multi-turn conversation")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    # First response
    first_response = client.responses.create({
        "model": "gpt-4.1",
        "input": "My name is Alice and I love hiking.",
        "store": True
    })
    print(f"First: {first_response.output_text}")

    # Continue conversation
    second_response = client.responses.create({
        "model": "gpt-4.1",
        "input": "What's my favorite activity?",
        "previous_response_id": first_response.id
    })
    print(f"Second: {second_response.output_text}")
    print()


def example_get_response():
    """Example 9: Getting a response by ID"""
    print("Example 9: Get response by ID")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    # First create a response
    response = client.responses.create({
        "model": "gpt-4.1",
        "input": "Hello, world!",
        "store": True
    })
    print(f"Created response with ID: {response.id}")

    # Retrieve it by ID
    retrieved = client.responses.get(response.id)
    print(f"Retrieved: {retrieved.output_text}")

    # Delete the response
    result = client.responses.delete(response.id)
    print(f"Deleted response: {result}")
    print()


def example_error_handling():
    """Example 10: Error handling"""
    print("Example 10: Error handling")
    print("-" * 40)

    client = tokenrouter.TokenRouter(api_key=api_key, base_url=base_url)

    try:
        response = client.responses.create({
            "model": "gpt-4.1",
            "input": "Test message",
            # Invalid parameter to trigger error
            "invalid_param": "test"
        })
    except TokenRouterError as e:
        print(f"Error occurred: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")

    # Rate limit handling example
    try:
        # This would trigger rate limit if you exceed your quota
        for i in range(5):
            response = client.responses.create({
                "model": "gpt-4.1",
                "input": f"Message {i}"
            })
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        if e.retry_after:
            print(f"Retry after {e.retry_after} seconds")
    print()


def main():
    """Run all examples"""
    print("=" * 50)
    print("TokenRouter SDK - Responses API Examples")
    print("=" * 50)
    print()

    try:
        # Run examples
        example_simple_response()
        example_with_instructions()
        example_structured_input()
        example_streaming()
        example_function_calling()
        example_json_response()
        example_temperature_control()
        example_conversation_state()
        example_get_response()
        example_error_handling()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()