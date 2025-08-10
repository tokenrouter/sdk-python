"""
Streaming example for TokenRouter SDK
"""

import os
from tokenrouter import Client


def main():
    # Initialize client
    client = Client(
        api_key=os.getenv("TOKENROUTER_API_KEY", "your-api-key"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    )
    
    print("TokenRouter SDK - Streaming Example")
    print("=" * 50)
    print("\nStreaming a short story...\n")
    
    try:
        # Create a streaming chat completion
        stream = client.chat.create(
            messages=[
                {"role": "system", "content": "You are a creative writer"},
                {"role": "user", "content": "Write a very short story (3 sentences) about a robot learning to paint"}
            ],
            model="auto",
            stream=True,
            temperature=0.8,
            max_tokens=150
        )
        
        # Process the stream
        full_response = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].get("delta", {}).get("content"):
                content = chunk.choices[0]["delta"]["content"]
                print(content, end="", flush=True)
                full_response += content
        
        print("\n\n" + "=" * 50)
        print(f"Total characters: {len(full_response)}")
        
    except KeyboardInterrupt:
        print("\n\nStreaming interrupted by user")
    except Exception as e:
        print(f"\nError during streaming: {e}")


if __name__ == "__main__":
    main()