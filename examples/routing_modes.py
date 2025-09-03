#!/usr/bin/env python3
"""
Example: Using routing modes with TokenRouter SDK
Demonstrates cost, quality, latency, and balanced routing strategies
"""

import os
import asyncio
from tokenrouter import TokenRouter, AsyncTokenRouter

def sync_routing_modes_example():
    """Demonstrate different routing modes with synchronous client"""
    print("TokenRouter Routing Modes Example (Sync)\n")
    
    # Initialize client
    client = TokenRouter(
        api_key=os.getenv("TOKENROUTER_API_KEY"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    )
    
    prompt = "Write a haiku about programming"
    messages = [{"role": "user", "content": prompt}]
    
    # 1. Cost-optimized routing
    print("1. COST MODE - Prioritizes cheaper models:")
    response = client.chat.completions.create(
        messages=messages,
        mode="cost",
        max_tokens=50
    )
    print(f"   Model: {response.model}")
    print(f"   Cost: ${response.cost_usd or 0:.6f}")
    print(f"   Response: {response.choices[0].message.content}\n")
    
    # 2. Quality-optimized routing
    print("2. QUALITY MODE - Prioritizes premium models:")
    response = client.chat.completions.create(
        messages=messages,
        mode="quality",
        max_tokens=50
    )
    print(f"   Model: {response.model}")
    print(f"   Cost: ${response.cost_usd or 0:.6f}")
    print(f"   Response: {response.choices[0].message.content}\n")
    
    # 3. Latency-optimized routing
    print("3. LATENCY MODE - Prioritizes fast response times:")
    response = client.chat.completions.create(
        messages=messages,
        mode="latency",
        max_tokens=50
    )
    print(f"   Model: {response.model}")
    print(f"   Latency: {response.latency_ms}ms")
    print(f"   Response: {response.choices[0].message.content}\n")
    
    # 4. Balanced routing (default)
    print("4. BALANCED MODE - Balances cost, quality, and speed:")
    response = client.chat.completions.create(
        messages=messages,
        mode="balanced",  # or omit for default
        max_tokens=50
    )
    print(f"   Model: {response.model}")
    print(f"   Cost: ${response.cost_usd or 0:.6f}")
    print(f"   Latency: {response.latency_ms}ms")
    print(f"   Response: {response.choices[0].message.content}\n")


async def async_routing_modes_example():
    """Demonstrate routing modes with async client"""
    print("TokenRouter Routing Modes Example (Async)\n")
    
    async with AsyncTokenRouter(
        api_key=os.getenv("TOKENROUTER_API_KEY"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    ) as client:
        
        # Run multiple requests concurrently with different modes
        tasks = [
            ("cost", "What is 2+2?"),
            ("quality", "Explain quantum computing"),
            ("latency", "Translate 'Hello' to Spanish"),
            ("balanced", "Write a Python function to reverse a string")
        ]
        
        async def process_with_mode(mode, prompt):
            response = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                mode=mode,
                max_tokens=100
            )
            return {
                "mode": mode,
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "model": response.model,
                "cost": response.cost_usd or 0,
                "latency": response.latency_ms
            }
        
        # Execute all requests concurrently
        results = await asyncio.gather(*[
            process_with_mode(mode, prompt) for mode, prompt in tasks
        ])
        
        # Display results
        print("Concurrent requests with different modes:\n")
        for result in results:
            print(f"Mode: {result['mode']:10} | Prompt: {result['prompt']:30}")
            print(f"  → Model: {result['model']:25} | Cost: ${result['cost']:.6f} | Latency: {result['latency']}ms\n")


def streaming_with_mode_example():
    """Demonstrate streaming with routing modes"""
    print("Streaming with Routing Mode Example\n")
    
    client = TokenRouter(
        api_key=os.getenv("TOKENROUTER_API_KEY"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    )
    
    # Stream with cost mode
    print("Streaming response (cost mode):")
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": "Tell me a joke"}],
        mode="cost",
        stream=True
    )
    
    for chunk in stream:
        delta = (chunk.choices[0].get("delta", {}) if chunk.choices else {})
        if delta.get("content"):
            print(delta["content"], end="", flush=True)
    print("\n")
    
    # Stream with quality mode
    print("Streaming response (quality mode):")
    stream = client.chat.completions.create(
        messages=[{"role": "user", "content": "Write a poem about AI"}],
        mode="quality",
        stream=True
    )
    
    for chunk in stream:
        delta = (chunk.choices[0].get("delta", {}) if chunk.choices else {})
        if delta.get("content"):
            print(delta["content"], end="", flush=True)
    print("\n")


def mode_selection_strategy():
    """Demonstrate when to use each routing mode"""
    print("Mode Selection Strategy Guide\n")
    
    client = TokenRouter(
        api_key=os.getenv("TOKENROUTER_API_KEY"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    )
    
    strategies = [
        {
            "scenario": "Bulk processing of simple queries",
            "mode": "cost",
            "example": "Categorize 1000 product descriptions",
            "prompt": "Is 'apple' a fruit? Answer yes or no."
        },
        {
            "scenario": "Complex analysis or creative writing",
            "mode": "quality",
            "example": "Write a technical whitepaper",
            "prompt": "Analyze the implications of quantum computing on cryptography"
        },
        {
            "scenario": "Real-time chat or autocomplete",
            "mode": "latency",
            "example": "Live customer support chat",
            "prompt": "Suggest next word: 'The weather today is'"
        },
        {
            "scenario": "General purpose queries",
            "mode": "balanced",
            "example": "Regular application usage",
            "prompt": "Summarize this paragraph in 3 bullet points"
        }
    ]
    
    for strategy in strategies:
        print(f"Scenario: {strategy['scenario']}")
        print(f"Recommended Mode: {strategy['mode'].upper()}")
        print(f"Example Use Case: {strategy['example']}")
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": strategy['prompt']}],
            mode=strategy['mode'],
            max_tokens=50
        )
        
        print(f"Selected Model: {response.model}")
        print(f"Cost: ${response.cost_usd or 0:.6f}")
        print(f"Latency: {response.latency_ms}ms")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("TOKENROUTER_API_KEY"):
        print("Please set TOKENROUTER_API_KEY environment variable")
        exit(1)
    
    # Run examples
    print("=" * 60)
    print("TokenRouter SDK - Routing Modes Examples")
    print("=" * 60 + "\n")
    
    # Synchronous examples
    sync_routing_modes_example()
    
    # Streaming example
    streaming_with_mode_example()
    
    # Mode selection guide
    mode_selection_strategy()
    
    # Async examples
    print("\n" + "=" * 60)
    asyncio.run(async_routing_modes_example())
    
    print("\nAll examples completed!")
