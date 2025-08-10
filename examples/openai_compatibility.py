"""
OpenAI SDK compatibility example for TokenRouter
"""

import os


def main():
    print("TokenRouter - OpenAI SDK Compatibility")
    print("=" * 50)
    
    # Get configuration
    api_key = os.getenv("TOKENROUTER_API_KEY", "your-tokenrouter-api-key")
    base_url = os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    
    print("\nThis example shows how to use TokenRouter with the OpenAI SDK")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    try:
        import openai
    except ImportError:
        print("\nOpenAI SDK not installed. Install it with:")
        print("pip install openai")
        return
    
    # Configure OpenAI client to use TokenRouter
    openai.api_key = api_key
    openai.api_base = f"{base_url}/v1"
    
    print("\n1. Chat Completion (auto routing):")
    print("-" * 30)
    try:
        # Use OpenAI SDK with TokenRouter's auto routing
        response = openai.ChatCompletion.create(
            model="auto",  # TokenRouter will choose the best model
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "What is 2+2?"}
            ],
            temperature=0.7
        )
        
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model used: {response.model}")
        print(f"Tokens: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Specific Model Request:")
    print("-" * 30)
    try:
        # Request a specific model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Request specific model
            messages=[
                {"role": "user", "content": "Write a haiku about coding"}
            ]
        )
        
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Streaming with OpenAI SDK:")
    print("-" * 30)
    try:
        # Streaming response
        stream = openai.ChatCompletion.create(
            model="auto",
            messages=[
                {"role": "user", "content": "Count from 1 to 3"}
            ],
            stream=True
        )
        
        print("Streaming: ", end="")
        for chunk in stream:
            if chunk.choices[0].delta.get("content"):
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n4. Function Calling:")
    print("-" * 30)
    try:
        # Function calling example
        functions = [
            {
                "name": "get_weather",
                "description": "Get the weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
        
        response = openai.ChatCompletion.create(
            model="auto",
            messages=[
                {"role": "user", "content": "What's the weather in San Francisco?"}
            ],
            functions=functions,
            function_call="auto"
        )
        
        message = response.choices[0].message
        if hasattr(message, "function_call") and message.function_call:
            print(f"Function call: {message.function_call.name}")
            print(f"Arguments: {message.function_call.arguments}")
        else:
            print(f"Response: {message.content}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("OpenAI compatibility examples completed!")
    print("\nNote: TokenRouter extends OpenAI's API with additional features:")
    print("  - model='auto' for intelligent routing")
    print("  - model_preferences parameter for preferred models")
    print("  - Additional response fields: cost_usd, latency_ms, routed_model")


if __name__ == "__main__":
    main()