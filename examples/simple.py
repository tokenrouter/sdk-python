"""
Simple example of using TokenRouter SDK
"""

import os
import tokenrouter

# Initialize client
client = tokenrouter.TokenRouter(
    api_key=os.environ.get("TOKENROUTER_API_KEY"),
    base_url=os.environ.get("TOKENROUTER_BASE_URL", "https://api.tokenrouter.io/api"),
)

# Create a simple response
response = client.responses.create({
    "model": "gpt-4.1",
    "input": "What is the capital of France?"
})

print("Response:", response.output_text)
print("Model:", response.model)
print("Usage:", response.usage)