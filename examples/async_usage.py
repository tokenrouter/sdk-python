"""
Async usage examples for TokenRouter SDK
"""

import asyncio
import os
from tokenrouter import AsyncTokenRouter


async def simple_completion(client: AsyncTokenRouter, prompt: str):
    """Simple async completion via legacy completions endpoint"""
    response = await client.completions.create(prompt=prompt, model="auto")
    # The legacy completions returns OpenAI text completion shape; extract text
    if isinstance(response, dict) and response.get("choices"):
        return response["choices"][0].get("text", "")
    return ""


async def chat_completion(client: AsyncTokenRouter):
    """Async chat completion"""
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What are the benefits of async programming?"}
        ],
        model="auto",
        max_tokens=150
    )
    return response.choices[0].message.content


async def batch_processing(client: AsyncTokenRouter):
    """Process multiple prompts concurrently"""
    prompts = [
        "What is machine learning?",
        "Explain quantum computing",
        "What is blockchain?",
        "Describe cloud computing",
        "What is artificial intelligence?"
    ]
    
    # Create tasks for all prompts
    tasks = [simple_completion(client, prompt) for prompt in prompts]
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    
    return list(zip(prompts, results))


async def streaming_example(client: AsyncTokenRouter):
    """Async streaming example"""
    print("Streaming response:")
    print("-" * 30)
    
    stream = await client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Count from 1 to 5 slowly"}
        ],
        model="auto",
        stream=True
    )
    
    full_response = ""
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].get("delta", {}).get("content"):
            content = chunk.choices[0]["delta"]["content"]
            print(content, end="", flush=True)
            full_response += content
    
    print("\n")
    return full_response


async def concurrent_operations(client: AsyncTokenRouter):
    """Run multiple operations concurrently"""
    tasks = [
        client.list_models(),
        client.get_costs(),
        client.get_analytics(),
        client.health_check()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


async def main():
    print("TokenRouter SDK - Async Examples")
    print("=" * 50)
    
    # Initialize async client
    async with AsyncTokenRouter(
        api_key=os.getenv("TOKENROUTER_API_KEY", "your-api-key"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "http://localhost:8000")
    ) as client:
        
        # Example 1: Simple async completion
        print("\n1. Simple Async Completion:")
        print("-" * 30)
        try:
            result = await simple_completion(client, "What is Python?")
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 2: Chat completion
        print("\n2. Async Chat Completion:")
        print("-" * 30)
        try:
            result = await chat_completion(client)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 3: Batch processing
        print("\n3. Batch Processing (Concurrent):")
        print("-" * 30)
        try:
            results = await batch_processing(client)
            for prompt, answer in results:
                print(f"\nQ: {prompt}")
                print(f"A: {answer[:100]}...")  # First 100 chars
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 4: Streaming
        print("\n4. Async Streaming:")
        print("-" * 30)
        try:
            await streaming_example(client)
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 5: Concurrent operations
        print("\n5. Concurrent API Operations:")
        print("-" * 30)
        try:
            models, costs, analytics, health = await concurrent_operations(client)
            
            if not isinstance(models, Exception):
                print(f"Models available: {len(models)}")
            else:
                print(f"Models error: {models}")
            
            if not isinstance(costs, Exception):
                print(f"Cost entries: {len(costs)}")
            else:
                print(f"Costs error: {costs}")
            
            if not isinstance(analytics, Exception):
                print(f"Total requests: {analytics.total_requests}")
            else:
                print(f"Analytics error: {analytics}")
            
            if not isinstance(health, Exception):
                print(f"Health status: {health.get('status', 'Unknown')}")
            else:
                print(f"Health error: {health}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Async examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
