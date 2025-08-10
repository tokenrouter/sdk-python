"""
TokenRouter SDK - Intelligent LLM Routing Client

A Python SDK for the TokenRouter API that provides intelligent routing
to multiple LLM providers with cost optimization.
"""

from .client import Client, AsyncClient
from .models import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionChoice,
    Usage,
    Model,
    ModelCosts,
)
from .exceptions import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
)

__version__ = "1.0.0"
__all__ = [
    "Client",
    "AsyncClient",
    "ChatCompletion",
    "ChatCompletionMessage",
    "ChatCompletionChoice",
    "Usage",
    "Model",
    "ModelCosts",
    "TokenRouterError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "APIConnectionError",
    "APIStatusError",
]