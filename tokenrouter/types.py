"""
Type definitions for TokenRouter SDK
"""

from typing import Dict, List, Optional, Any, Union, Literal, TypedDict
from dataclasses import dataclass, field


class ResponsesCreateParams(TypedDict, total=False):
    """Parameters for creating a response"""
    input: Union[str, List["InputItem"]]  # Required
    model: Optional[str]
    instructions: Optional[str]
    max_output_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    stream: Optional[bool]
    tools: Optional[List["Tool"]]
    tool_choice: Optional[Union[str, Dict[str, Any]]]
    text: Optional[Dict[str, Any]]
    previous_response_id: Optional[str]
    store: Optional[bool]
    metadata: Optional[Dict[str, Any]]


class InputItem(TypedDict):
    """Input item for a response"""
    type: str
    id: Optional[str]
    text: Optional[str]
    role: Optional[str]
    audio: Optional[Dict[str, Any]]
    content: Optional[List["ContentItem"]]


class ContentItem(TypedDict):
    """Content item within input or output"""
    type: str
    text: Optional[str]
    input_text: Optional[Dict[str, Any]]
    output_text: Optional[Dict[str, Any]]


class OutputItem(TypedDict):
    """Output item in response"""
    type: str
    id: Optional[str]
    index: Optional[int]
    content: Optional[List[ContentItem]]
    tool_calls: Optional[List["ToolCall"]]


class ToolCall(TypedDict):
    """Tool call in output"""
    type: str
    id: Optional[str]
    function: Optional["FunctionCall"]


class FunctionCall(TypedDict):
    """Function call details"""
    name: str
    arguments: str


class Tool(TypedDict):
    """Tool definition"""
    type: str
    function: Optional["FunctionTool"]


class FunctionTool(TypedDict):
    """Function tool definition"""
    name: str
    description: Optional[str]
    parameters: Optional[Dict[str, Any]]


class Usage(TypedDict):
    """Usage statistics"""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_token_details: Optional[Dict[str, Any]]
    output_token_details: Optional[Dict[str, Any]]


@dataclass
class Response:
    """Response from the API"""
    id: str
    object: str = "realtime.response"
    created: Optional[int] = None
    model: Optional[str] = None
    usage: Optional[Usage] = None
    output: List[OutputItem] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    status_details: Optional[Dict[str, Any]] = None
    output_text: Optional[str] = None  # Convenience property


@dataclass
class ResponseDelta:
    """Delta update for streaming response"""
    output: Optional[List[OutputItem]] = None


@dataclass
class ResponseStreamEvent:
    """Event in streaming response"""
    type: str
    response: Optional[Response] = None
    delta: Optional[ResponseDelta] = None
    item: Optional[OutputItem] = None
    event_id: Optional[str] = None
    rate_limits: Optional[List[Dict[str, Any]]] = None


class InputItemsList(TypedDict):
    """List of input items"""
    object: str
    data: List[InputItem]