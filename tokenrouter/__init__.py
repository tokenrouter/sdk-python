"""
TokenRouter SDK - Intelligent LLM Routing Client

A Python SDK for the TokenRouter API that provides intelligent routing
to multiple LLM providers with cost optimization.
"""

from .client import TokenRouter, AsyncTokenRouter
from .models import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionChoice,
    Usage,
)
from .exceptions import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
)

__version__ = "1.0.5"
__all__ = [
    "TokenRouter",
    "AsyncTokenRouter",
    "ChatCompletion",
    "ChatCompletionMessage",
    "ChatCompletionChoice",
    "Usage",
    "TokenRouterError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "APIConnectionError",
    "APIStatusError",
]
