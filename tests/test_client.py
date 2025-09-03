"""
Tests for TokenRouter SDK Client
"""

import os
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import httpx

from tokenrouter import (
    TokenRouter,
    AsyncTokenRouter,
    ChatCompletion,
    ChatCompletionMessage,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
)


class TestClient:
    """Test synchronous client"""
    
    def test_client_init_with_api_key(self):
        """Test client initialization with API key"""
        client = TokenRouter(api_key="test-key", base_url="http://localhost:8000")
        assert client.api_key == "test-key"
        assert client.base_url == "http://localhost:8000"
    
    def test_client_init_from_env(self):
        """Test client initialization from environment variables"""
        with patch.dict(os.environ, {"TOKENROUTER_API_KEY": "env-key", "TOKENROUTER_BASE_URL": "https://api.example.com"}):
            client = TokenRouter()
            assert client.api_key == "env-key"
            assert client.base_url == "https://api.example.com"
    
    def test_client_init_no_api_key(self):
        """Test client initialization without API key raises error"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError):
                TokenRouter()
    
    @patch("httpx.Client.request")
    def test_chat_completion(self, mock_request):
        """Test chat completion"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "chat-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_request.return_value = mock_response
        
        client = TokenRouter(api_key="test-key")
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-3.5-turbo"
        )
        
        assert isinstance(response, ChatCompletion)
        assert response.id == "chat-123"
        assert response.content == "Hello! How can I help you?"
        assert response.usage.total_tokens == 30
    
    # Deprecated shorthand removed: use chat.completions.create instead
    
    # Removed utility endpoints per routing-only scope
    
    @patch("httpx.Client.request")
    def test_error_handling_401(self, mock_request):
        """Test 401 authentication error handling"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid API key"}
        mock_request.return_value = mock_response
        mock_request.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=Mock(),
            response=mock_response
        )
        
        client = TokenRouter(api_key="invalid-key")
        with pytest.raises(AuthenticationError) as exc_info:
            client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="auto"
            )
        assert "Invalid API key" in str(exc_info.value)
    
    @patch("httpx.Client.request")
    def test_error_handling_429(self, mock_request):
        """Test 429 rate limit error handling"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"detail": "Rate limit exceeded"}
        mock_request.return_value = mock_response
        mock_request.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=Mock(),
            response=mock_response
        )
        
        client = TokenRouter(api_key="test-key")
        with pytest.raises(RateLimitError) as exc_info:
            client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="auto"
            )
        assert exc_info.value.retry_after == 60
    
    @patch("httpx.Client.request")
    def test_retry_on_500_errors(self, mock_request):
        """Test retry logic for 500 errors"""
        # First two calls fail with 500, third succeeds
        mock_response_500 = Mock()
        mock_response_500.status_code = 500
        mock_response_500.json.return_value = {"detail": "Server error"}
        
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "id": "chat-ok",
            "object": "chat.completion",
            "created": 123,
            "model": "auto",
            "choices": [{
              "index": 0,
              "message": {"role": "assistant", "content": "ok"},
              "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}
        }
        
        mock_request.side_effect = [
            httpx.HTTPStatusError("500 Server Error", request=Mock(), response=mock_response_500),
            httpx.HTTPStatusError("500 Server Error", request=Mock(), response=mock_response_500),
            mock_response_200
        ]
        
        client = TokenRouter(api_key="test-key", base_url="http://localhost:8000", max_retries=3)
        with patch("time.sleep"):  # Mock sleep to speed up test
            result = client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="auto"
            )
        assert result.id == "chat-ok"
        assert mock_request.call_count == 3


class TestAsyncClient:
    """Test asynchronous client"""
    
    @pytest.mark.asyncio
    async def test_async_client_init(self):
        """Test async client initialization"""
        client = AsyncTokenRouter(api_key="test-key", base_url="http://localhost:8000")
        assert client.api_key == "test-key"
        await client.close()
    
    @pytest.mark.asyncio
    @patch("httpx.AsyncClient.request")
    async def test_async_chat_completion(self, mock_request):
        """Test async chat completion"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "chat-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Async response"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_request.return_value = mock_response
        
        async with AsyncTokenRouter(api_key="test-key") as client:
            response = await client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model="gpt-3.5-turbo"
            )
            
            assert isinstance(response, ChatCompletion)
            assert response.content == "Async response"
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test async context manager"""
        async with AsyncTokenRouter(api_key="test-key") as client:
            assert client.api_key == "test-key"
        # Client should be closed after context


class TestModels:
    """Test model classes"""
    
    def test_chat_completion_message(self):
        """Test ChatCompletionMessage"""
        msg = ChatCompletionMessage(
            role="user",
            content="Test message"
        )
        
        assert msg.role == "user"
        assert msg.content == "Test message"
        
        msg_dict = msg.to_dict()
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Test message"
        
        msg2 = ChatCompletionMessage.from_dict(msg_dict)
        assert msg2.role == "user"
        assert msg2.content == "Test message"
    
    def test_chat_completion_from_dict(self):
        """Test ChatCompletion from dict"""
        data = {
            "id": "chat-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Test response"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            },
            "cost_usd": 0.001,
            "latency_ms": 250
        }
        
        completion = ChatCompletion.from_dict(data)
        assert completion.id == "chat-123"
        assert completion.content == "Test response"
        assert completion.usage.total_tokens == 30
        assert completion.cost_usd == 0.001
        assert completion.latency_ms == 250


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
