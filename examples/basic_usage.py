"""
Basic usage examples for TokenRouter SDK
"""

from tokenrouter import TokenRouter
import os


def main():
    # Initialize client (uses TOKENROUTER_API_KEY from environment)
    client = TokenRouter(
        api_key=os.getenv("TOKENROUTER_API_KEY", "your-api-key"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    )
    
    print("=" * 50)
    print("TokenRouter SDK - Basic Routing Examples")
    print("=" * 50)
    
    # Example 1: Native route completion (/route)
    print("\n1. Simple Completion:")
    print("-" * 30)
    response = client.create(
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        model="auto",
        mode="balanced"
    )
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model used: {response.model}")
    print(f"Tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
    
    # Example 2: Chat completions (/v1/chat/completions)
    print("\n2. Chat Completions:")
    print("-" * 30)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Explain photosynthesis in 2 sentences"}
        ],
        model="auto",  # Let TokenRouter choose the best model
        temperature=0.7
    )
    print(f"Response: {response.choices[0].message.content}")
    
    # Example 3: Legacy completions (/v1/completions)
    print("\n3. Legacy Completions:")
    print("-" * 30)
    resp = client.completions.create(
        prompt="Say this is a test",
        model="auto"
    )
    print(f"Response (text): {resp['choices'][0].get('text', '')}")
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
