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
    print("TokenRouter SDK - Basic Usage Examples")
    print("=" * 50)
    
    # Example 1: Simple completion
    print("\n1. Simple Completion:")
    print("-" * 30)
    response = client.completions("What is the capital of France?")
    print(f"Response: {response.content}")
    print(f"Model used: {response.model}")
    print(f"Tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
    
    # Example 2: Chat completion
    print("\n2. Chat Completion:")
    print("-" * 30)
    response = client.chat.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Explain photosynthesis in 2 sentences"}
        ],
        model="auto",  # Let TokenRouter choose the best model
        temperature=0.7
    )
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.6f}" if response.cost_usd else "Cost: N/A")
    print(f"Latency: {response.latency_ms}ms" if response.latency_ms else "Latency: N/A")
    
    # Example 3: Model preferences
    print("\n3. With Model Preferences:")
    print("-" * 30)
    response = client.chat.create(
        messages=[
            {"role": "user", "content": "Write a haiku about programming"}
        ],
        model_preferences=["claude-3-haiku", "gpt-3.5-turbo"],
        max_tokens=50
    )
    print(f"Response: {response.content}")
    print(f"Routed to: {response.routed_model}" if response.routed_model else "Model: Unknown")
    
    # Example 4: List available models
    print("\n4. Available Models:")
    print("-" * 30)
    try:
        models = client.list_models()
        for model in models[:5]:  # Show first 5 models
            print(f"  - {model.id} ({model.provider})")
            if model.context_window:
                print(f"    Context: {model.context_window:,} tokens")
    except Exception as e:
        print(f"  Error listing models: {e}")
    
    # Example 5: Get costs
    print("\n5. Model Costs:")
    print("-" * 30)
    try:
        costs = client.get_costs()
        for model, cost in list(costs.items())[:5]:  # Show first 5
            print(f"  - {model}: ${cost:.6f}/1k tokens")
    except Exception as e:
        print(f"  Error getting costs: {e}")
    
    # Example 6: Analytics
    print("\n6. Usage Analytics:")
    print("-" * 30)
    try:
        analytics = client.get_analytics()
        print(f"  Total requests: {analytics.total_requests}")
        print(f"  Total tokens: {analytics.total_tokens:,}")
        print(f"  Total cost: ${analytics.total_cost_usd:.4f}")
        print(f"  Avg latency: {analytics.average_latency_ms:.0f}ms")
        print(f"  Cache hit rate: {analytics.cache_hit_rate:.1%}")
    except Exception as e:
        print(f"  Error getting analytics: {e}")
    
    # Example 7: Health check
    print("\n7. API Health Check:")
    print("-" * 30)
    try:
        health = client.health_check()
        print(f"  Status: {health.get('status', 'Unknown')}")
        if 'providers' in health:
            print(f"  Available providers: {', '.join(health['providers'])}")
    except Exception as e:
        print(f"  Error checking health: {e}")
    
    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()