"""
TokenRouter SDK Client
"""

import os
import time
import json as jsonlib
import asyncio
from typing import Optional, Dict, Any, List, Union, AsyncIterator, Iterator
from urllib.parse import urljoin
import httpx
from httpx import Response, HTTPStatusError
from typing import TypedDict

from .models import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionChunk,
)
from .exceptions import (
    TokenRouterError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    APIConnectionError,
    APIStatusError,
    TimeoutError,
    QuotaExceededError,
)
from .crypto import encrypt_provider_keys_header


class TextCompletionChoice(TypedDict, total=False):
    text: str
    index: int
    logprobs: Optional[Dict[str, Any]]
    finish_reason: Optional[str]


class TextCompletion(TypedDict, total=False):
    id: str
    object: str
    created: int
    model: str
    choices: List[TextCompletionChoice]
    usage: Optional[Dict[str, int]]


class BaseClient:
    """Base client with common functionality"""

    DEFAULT_BASE_URL = "https://api.tokenrouter.io"
    DEFAULT_TIMEOUT = 60.0
    DEFAULT_MAX_RETRIES = 3

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key or os.environ.get("TOKENROUTER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set TOKENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = (base_url or os.environ.get("TOKENROUTER_BASE_URL", self.DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "tokenrouter-python/1.0.5",
        }
        if headers:
            self.headers.update(headers)
        # Cache for public key
        self._tr_public_key_pem: Optional[str] = None

    def _load_env_provider_keys(self) -> Dict[str, str]:
        """Load provider keys from environment or a local .env file in CWD, if present."""
        keys: Dict[str, str] = {}
        # Try reading .env for dev/CI if not already in env
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass
        mapping = {
            "openai": os.environ.get("OPENAI_API_KEY"),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
            "mistral": os.environ.get("MISTRAL_API_KEY"),
            "deepseek": os.environ.get("DEEPSEEK_API_KEY"),
            "google": os.environ.get("GEMINI_API_KEY"),
            "meta": os.environ.get("META_API_KEY"),
        }
        for k, v in mapping.items():
            if v:
                keys[k] = v
        return keys

    def _fetch_public_key(self) -> str:
        if self._tr_public_key_pem:
            return self._tr_public_key_pem
        url = urljoin(self.base_url, "/.well-known/tr-public-key")
        try:
            resp = httpx.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            pem = data.get("public_key_pem")
            if not pem:
                raise ValueError("missing public_key_pem")
            self._tr_public_key_pem = pem
            return pem
        except Exception as e:
            raise APIConnectionError(f"Failed to obtain public key: {e}")

    def _build_secure_headers(self, key_mode: Optional[str]) -> Dict[str, str]:
        mode = (key_mode or "auto").lower()
        if mode == "stored":
            return {}
        provider_keys = self._load_env_provider_keys()
        if not provider_keys:
            return {}
        pem = self._fetch_public_key()
        header_value = encrypt_provider_keys_header(provider_keys, pem)
        return {"X-TR-Provider-Keys": header_value}

    def _handle_response_error(self, response: Response) -> None:
        """Handle HTTP response errors"""
        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                response.status_code,
                headers=dict(response.headers),
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code == 400:
            raise InvalidRequestError(message, response.status_code)
        elif response.status_code == 403:
            if "quota" in message.lower():
                raise QuotaExceededError(message, response.status_code)
            raise AuthenticationError(message, response.status_code)
        elif response.status_code >= 500:
            raise APIStatusError(message, response.status_code)
        else:
            raise TokenRouterError(message, response.status_code)


class ChatCompletions:
    """Chat completions interface (/v1/chat/completions)"""

    def __init__(self, client: "TokenRouter"):
        self.client = client

    def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        n: Optional[int] = None,
        logprobs: Optional[bool] = None,
        echo: Optional[bool] = None,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,  # cost | quality | latency | balanced
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:

        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }

        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if n is not None:
            payload["n"] = n
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if echo is not None:
            payload["echo"] = echo
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if seed is not None:
            payload["seed"] = seed

        payload.update(kwargs)
        if stream:
            return self.client._stream_request("/v1/chat/completions", payload)
        response = self.client._request("POST", "/v1/chat/completions", json=payload)
        return ChatCompletion.from_dict(response)


class LegacyCompletions:
    """OpenAI legacy completions interface (/v1/completions)"""

    def __init__(self, client: "TokenRouter"):
        self.client = client

    def create(
        self,
        prompt: Union[str, List[Union[str, int, List[int]]]],
        model: str = "auto",
        mode: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user: Optional[str] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> Union[TextCompletion, Iterator[Dict[str, Any]]]:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if mode is not None:
            payload["mode"] = mode
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if user is not None:
            payload["user"] = user
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        payload.update(kwargs)
        if stream:
            return self.client._stream_request_raw("/v1/completions", payload)
        return self.client._request("POST", "/v1/completions", json=payload)


class ChatNamespace:
    """Namespace for chat APIs, matching OpenAI style: client.chat.completions.create"""

    def __init__(self, client: "TokenRouter"):
        self.completions = ChatCompletions(client)


class TokenRouter(BaseClient):
    """Synchronous TokenRouter client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        # Namespaced routes matching OpenAI style
        self.chat = ChatNamespace(self)
        self.completions = LegacyCompletions(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self) -> None:
        self.client.close()

    # Native TokenRouter endpoint: /route
    def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        key_mode: Optional[str] = None,
        **kwargs,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        elif max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if key_mode is not None:
            payload["key_mode"] = key_mode
        payload.update(kwargs)
        extra_headers = self._build_secure_headers(key_mode)
        if stream:
            return self._stream_request("/route", payload, extra_headers)
        response = self._request("POST", "/route", json=payload, extra_headers=extra_headers)
        return ChatCompletion.from_dict(response)

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, path)
        try:
            headers = self.headers.copy()
            if extra_headers:
                headers.update(extra_headers)
            response = self.client.request(method, url, json=json, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {e}")
        except HTTPStatusError as e:
            if retry_count < self.max_retries and e.response.status_code >= 500:
                time.sleep(2 ** retry_count)
                return self._request(method, path, json, params, retry_count + 1)
            self._handle_response_error(e.response)
        except Exception as e:
            raise TokenRouterError(f"Unexpected error: {e}")

    def _stream_request(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Iterator[ChatCompletionChunk]:
        url = urljoin(self.base_url, path)
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        with self.client.stream("POST", url, json=json, headers=headers) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    chunk = ChatCompletionChunk.from_sse_data(data)
                    if chunk:
                        yield chunk

    def _stream_request_raw(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Iterator[Dict[str, Any]]:
        url = urljoin(self.base_url, path)
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        with self.client.stream("POST", url, json=json, headers=headers) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield jsonlib.loads(data)
                    except Exception:
                        continue

    # Strict to Request_1: no additional utility endpoints


class AsyncChatCompletions:
    def __init__(self, client: "AsyncTokenRouter"):
        self.client = client

    async def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        n: Optional[int] = None,
        logprobs: Optional[bool] = None,
        echo: Optional[bool] = None,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        **kwargs,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if n is not None:
            payload["n"] = n
        if logprobs is not None:
            payload["logprobs"] = logprobs
        if echo is not None:
            payload["echo"] = echo
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if seed is not None:
            payload["seed"] = seed
        payload.update(kwargs)
        if stream:
            return self.client._stream_request("/v1/chat/completions", payload)
        response = await self.client._request("POST", "/v1/chat/completions", json=payload)
        return ChatCompletion.from_dict(response)


class AsyncLegacyCompletions:
    def __init__(self, client: "AsyncTokenRouter"):
        self.client = client

    async def create(
        self,
        prompt: Union[str, List[Union[str, int, List[int]]]],
        model: str = "auto",
        mode: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user: Optional[str] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs,
    ) -> Union[TextCompletion, AsyncIterator[Dict[str, Any]]]:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if mode is not None:
            payload["mode"] = mode
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if user is not None:
            payload["user"] = user
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        payload.update(kwargs)
        if stream:
            return self.client._stream_request_raw("/v1/completions", payload)
        return await self.client._request("POST", "/v1/completions", json=payload)


class AsyncChatNamespace:
    """Namespace for async chat APIs, matching OpenAI style: client.chat.completions.create"""

    def __init__(self, client: "AsyncTokenRouter"):
        self.completions = AsyncChatCompletions(client)


class AsyncTokenRouter(BaseClient):
    """Asynchronous TokenRouter client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.chat = AsyncChatNamespace(self)
        self.completions = AsyncLegacyCompletions(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def close(self) -> None:
        await self.client.aclose()

    # Native TokenRouter endpoint: /route (async)
    async def create(
        self,
        messages: List[Union[Dict[str, Any], ChatCompletionMessage]],
        model: str = "auto",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_completion_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        model_preferences: Optional[List[str]] = None,
        mode: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        key_mode: Optional[str] = None,
        **kwargs,
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        messages_dict: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatCompletionMessage):
                messages_dict.append(msg.to_dict())
            else:
                messages_dict.append(msg)

        payload: Dict[str, Any] = {
            "messages": messages_dict,
            "model": model,
            "stream": stream,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_completion_tokens is not None:
            payload["max_completion_tokens"] = max_completion_tokens
        elif max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop is not None:
            payload["stop"] = stop
        if user is not None:
            payload["user"] = user
        if model_preferences is not None:
            payload["model_preferences"] = model_preferences
        if mode is not None:
            payload["mode"] = mode
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if response_format is not None:
            payload["response_format"] = response_format
        if key_mode is not None:
            payload["key_mode"] = key_mode
        payload.update(kwargs)
        extra_headers = self._build_secure_headers(key_mode)
        if stream:
            return self._stream_request("/route", payload, extra_headers)
        response = await self._request("POST", "/route", json=payload, extra_headers=extra_headers)
        return ChatCompletion.from_dict(response)

    async def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = urljoin(self.base_url, path)
        try:
            headers = self.headers.copy()
            if extra_headers:
                headers.update(extra_headers)
            response = await self.client.request(method, url, json=json, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}")
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Connection failed: {e}")
        except HTTPStatusError as e:
            if retry_count < self.max_retries and e.response.status_code >= 500:
                await asyncio.sleep(2 ** retry_count)
                return await self._request(method, path, json, params, retry_count + 1)
            self._handle_response_error(e.response)
        except Exception as e:
            raise TokenRouterError(f"Unexpected error: {e}")

    async def _stream_request(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> AsyncIterator[ChatCompletionChunk]:
        url = urljoin(self.base_url, path)
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        async with self.client.stream("POST", url, json=json, headers=headers) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    chunk = ChatCompletionChunk.from_sse_data(data)
                    if chunk:
                        yield chunk

    async def _stream_request_raw(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        url = urljoin(self.base_url, path)
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        async with self.client.stream("POST", url, json=json, headers=headers) as response:
            try:
                response.raise_for_status()
            except HTTPStatusError:
                self._handle_response_error(response)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        yield jsonlib.loads(data)
                    except Exception:
                        continue
