"""
TokenRouter SDK Client
OpenAI Responses API Compatible
"""

import os
import json
import time
from typing import Optional, Dict, Any, AsyncIterator, Iterator, Union
from dataclasses import asdict
import httpx

from .types import (
    ResponsesCreateParams,
    Response,
    ResponseStreamEvent,
    OutputItem,
    InputItemsList,
    ResponseDelta,
)
from .errors import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
    QuotaExceededError,
)


class TokenRouter:
    """TokenRouter client - OpenAI Responses API compatible"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 60.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
    ):
        """
        Initialize TokenRouter client

        Args:
            api_key: API key for TokenRouter. Defaults to TOKENROUTER_API_KEY env var
            base_url: Base URL for API. Defaults to https://api.tokenrouter.io/api
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            headers: Additional headers to include in requests
            verify_ssl: Whether to verify SSL certificates (set False for testing)
        """
        self.api_key = api_key or os.environ.get("TOKENROUTER_API_KEY", "")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set TOKENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = (
            base_url or os.environ.get("TOKENROUTER_BASE_URL", "https://api.tokenrouter.io/api")
        ).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Set up headers
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "tokenrouter-python/1.0.9",
        }
        if headers:
            self._headers.update(headers)

        # Create HTTP client
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._headers,
            verify=verify_ssl,
        )

        # Create responses namespace
        self.responses = ResponsesNamespace(self)

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from API"""
        status_code = response.status_code
        try:
            data = response.json()
            message = data.get("detail") or data.get("error") or response.text
        except:
            data = None
            message = response.text or response.reason_phrase

        headers = dict(response.headers)

        if status_code == 401:
            raise AuthenticationError(message, status_code, data, headers)
        elif status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise RateLimitError(
                message, status_code, data, headers,
                int(retry_after) if retry_after else None
            )
        elif status_code == 400:
            raise InvalidRequestError(message, status_code, data, headers)
        elif status_code == 403:
            if "quota" in message.lower():
                raise QuotaExceededError(message, status_code, data, headers)
            raise AuthenticationError(message, status_code, data, headers)
        elif status_code >= 500:
            raise APIStatusError(message, status_code, data, headers)
        else:
            raise TokenRouterError(message, status_code, data, headers)

    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> Any:
        """Make HTTP request with retries"""
        try:
            response = self._client.request(
                method=method,
                url=path,
                json=json_data,
                params=params,
            )

            if response.status_code >= 400:
                if retry_count < self.max_retries and response.status_code >= 500:
                    time.sleep(2 ** retry_count)
                    return self._request(method, path, json_data, params, retry_count + 1)
                self._handle_error_response(response)

            return response.json()

        except httpx.TimeoutException:
            raise APIConnectionError("Request timed out")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {str(e)}")
        except httpx.HTTPError as e:
            raise TokenRouterError(f"Request failed: {str(e)}")

    def _stream(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Iterator[ResponseStreamEvent]:
        """Make streaming HTTP request"""
        try:
            with self._client.stream(
                method=method,
                url=path,
                json=json_data,
                params=params,
            ) as response:
                if response.status_code >= 400:
                    self._handle_error_response(response)

                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event_data = json.loads(data)
                            # Debug: print raw event data
                            # print(f"DEBUG: Raw event data: {event_data}")
                            yield self._parse_stream_event(event_data)
                        except json.JSONDecodeError:
                            continue

        except httpx.TimeoutException:
            raise APIConnectionError("Request timed out")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {str(e)}")
        except httpx.HTTPError as e:
            raise TokenRouterError(f"Request failed: {str(e)}")

    def _parse_stream_event(self, data: Any) -> ResponseStreamEvent:
        """Parse streaming event data"""
        # Handle case where data is a list (delta chunks)
        if isinstance(data, list):
            # This is a delta output array
            event = ResponseStreamEvent(type="response.delta")
            event.delta = ResponseDelta(output=data)
            return event

        # Handle None or other non-dict data
        if not isinstance(data, dict):
            # Fallback for unexpected data
            event = ResponseStreamEvent(type="unknown")
            return event

        # Handle simple delta format: {'index': 0, 'delta': {'type': 'text', 'text': 'Hello'}}
        if "delta" in data and "index" in data:
            delta_content = data["delta"]
            if isinstance(delta_content, dict) and delta_content.get("type") == "text":
                # Create a proper output structure for text delta
                output_item = {
                    "type": "message",
                    "content": [
                        {
                            "type": "text",
                            "text": delta_content.get("text", "")
                        }
                    ]
                }
                event = ResponseStreamEvent(type="response.delta")
                event.delta = ResponseDelta(output=[output_item])
                return event

        # Handle usage stats
        if "input_tokens" in data or "output_tokens" in data or "total_tokens" in data:
            # This is a usage update
            event = ResponseStreamEvent(type="usage")
            return event

        # Standard response event handling
        event = ResponseStreamEvent(type=data.get("type", ""))

        if "response" in data:
            response_data = data["response"]
            event.response = Response(
                id=response_data.get("id", ""),
                object=response_data.get("object", "realtime.response"),
                created=response_data.get("created"),
                model=response_data.get("model"),
                usage=response_data.get("usage"),
                output=response_data.get("output", []),
                metadata=response_data.get("metadata"),
                status=response_data.get("status"),
                status_details=response_data.get("status_details"),
            )

        if "delta" in data and "index" not in data:
            delta_data = data["delta"]
            # Handle delta data which could be dict or already processed
            if isinstance(delta_data, dict):
                event.delta = ResponseDelta(
                    output=delta_data.get("output"),
                )
            else:
                event.delta = ResponseDelta(output=delta_data)

        if "item" in data:
            event.item = data["item"]

        event.event_id = data.get("event_id")
        event.rate_limits = data.get("rate_limits")

        return event

    def close(self):
        """Close the HTTP client"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ResponsesNamespace:
    """Namespace for responses operations"""

    def __init__(self, client: TokenRouter):
        self._client = client

    def create(
        self,
        params: Optional[Union[ResponsesCreateParams, Dict[str, Any]]] = None,
        **kwargs
    ) -> Union[Response, Iterator[ResponseStreamEvent]]:
        """
        Create a model response

        Args:
            params: Parameters for creating the response (dict or keyword args)
            **kwargs: Alternative way to pass parameters as keyword arguments

        Returns:
            Response object or stream of ResponseStreamEvent
        """
        # Handle both dict params and keyword arguments
        if params is not None:
            # If params provided, use it (could be dict or TypedDict)
            if isinstance(params, dict):
                request_params = params
            else:
                request_params = dict(params)
        else:
            # Use keyword arguments
            request_params = kwargs

        # Check if streaming
        if request_params.get("stream"):
            return self._client._stream("POST", "/v1/responses", json_data=request_params)

        # Regular request
        response_data = self._client._request("POST", "/v1/responses", json_data=request_params)

        # Create Response object
        response = Response(
            id=response_data.get("id", ""),
            object=response_data.get("object", "realtime.response"),
            created=response_data.get("created"),
            model=response_data.get("model"),
            usage=response_data.get("usage"),
            output=response_data.get("output", []),
            metadata=response_data.get("metadata"),
            status=response_data.get("status"),
            status_details=response_data.get("status_details"),
        )

        # Add convenience property output_text
        response.output_text = self._extract_output_text(response)

        return response

    def get(self, response_id: str) -> Response:
        """
        Get a response by ID

        Args:
            response_id: The ID of the response to retrieve

        Returns:
            Response object
        """
        response_data = self._client._request("GET", f"/v1/responses/{response_id}")

        response = Response(
            id=response_data.get("id", ""),
            object=response_data.get("object", "realtime.response"),
            created=response_data.get("created"),
            model=response_data.get("model"),
            usage=response_data.get("usage"),
            output=response_data.get("output", []),
            metadata=response_data.get("metadata"),
            status=response_data.get("status"),
            status_details=response_data.get("status_details"),
        )

        response.output_text = self._extract_output_text(response)

        return response

    def delete(self, response_id: str) -> Dict[str, Any]:
        """
        Delete a response

        Args:
            response_id: The ID of the response to delete

        Returns:
            Deletion confirmation
        """
        return self._client._request("DELETE", f"/v1/responses/{response_id}")

    def cancel(self, response_id: str) -> Response:
        """
        Cancel a background response

        Args:
            response_id: The ID of the response to cancel

        Returns:
            Updated Response object
        """
        response_data = self._client._request("POST", f"/v1/responses/{response_id}/cancel")

        response = Response(
            id=response_data.get("id", ""),
            object=response_data.get("object", "realtime.response"),
            created=response_data.get("created"),
            model=response_data.get("model"),
            usage=response_data.get("usage"),
            output=response_data.get("output", []),
            metadata=response_data.get("metadata"),
            status=response_data.get("status"),
            status_details=response_data.get("status_details"),
        )

        response.output_text = self._extract_output_text(response)

        return response

    def list_input_items(self, response_id: str) -> InputItemsList:
        """
        List input items for a response

        Args:
            response_id: The ID of the response

        Returns:
            InputItemsList object
        """
        data = self._client._request("GET", f"/v1/responses/{response_id}/input_items")
        return data

    def _extract_output_text(self, response: Response) -> str:
        """Extract text from response output"""
        texts = []
        for item in response.output or []:
            if item.get("type") == "message" and item.get("content"):
                for content in item["content"]:
                    if content.get("type") == "output_text" and content.get("text"):
                        texts.append(content["text"])
        return "".join(texts)