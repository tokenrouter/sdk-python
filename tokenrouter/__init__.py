"""
TokenRouter SDK - OpenAI Responses API Compatible Client
"""

from .client import TokenRouter
from .errors import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
    QuotaExceededError,
)
from .types import (
    ResponsesCreateParams,
    Response,
    ResponseStreamEvent,
    InputItem,
    OutputItem,
    ContentItem,
    ToolCall,
    FunctionCall,
    Tool,
    FunctionTool,
)

__version__ = "1.0.15"
__all__ = [
    "TokenRouter",
    "TokenRouterError",
    "AuthenticationError",
    "RateLimitError",
    "InvalidRequestError",
    "APIConnectionError",
    "APIStatusError",
    "QuotaExceededError",
    "ResponsesCreateParams",
    "Response",
    "ResponseStreamEvent",
    "InputItem",
    "OutputItem",
    "ContentItem",
    "ToolCall",
    "FunctionCall",
    "Tool",
    "FunctionTool",
]

# Default export for OpenAI-like usage
default = TokenRouter