"""
LLM 模块的单元测试
"""

import pytest
from unittest.mock import Mock, patch
from ascii_chart.llm.base import BaseLLMClient, ChatMessage, LLMError
from ascii_chart.llm.openai_client import OpenAIClient
from ascii_chart.llm.anthropic_client import AnthropicClient


class TestChatMessage:
    """ChatMessage 测试"""

    def test_message_creation(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_to_dict(self):
        msg = ChatMessage(role="assistant", content="Hi there")
        result = msg.to_dict()
        assert result == {"role": "assistant", "content": "Hi there"}


class TestOpenAIClient:
    """OpenAI 客户端测试"""

    def test_client_initialization(self):
        client = OpenAIClient(
            base_url="https://api.openai.com/v1",
            api_key="test-key",
            model="gpt-4",
        )
        assert client.base_url == "https://api.openai.com/v1"
        assert client.api_key == "test-key"
        assert client.model == "gpt-4"

    def test_client_without_api_key(self):
        """测试不提供 API key 时的行为"""
        client = OpenAIClient(api_key="")
        with pytest.raises(LLMError):
            client.chat([ChatMessage(role="user", content="Hello")])

    @patch("requests.Session.post")
    def test_chat_success(self, mock_post):
        """测试成功调用"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": "Test response"}}
            ]
        }
        mock_post.return_value = mock_response

        client = OpenAIClient(api_key="test-key")
        result = client.chat([ChatMessage(role="user", content="Hello")])

        assert result == "Test response"
        mock_post.assert_called_once()

    @patch("requests.Session.post")
    def test_chat_timeout(self, mock_post):
        """测试超时"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        client = OpenAIClient(api_key="test-key")
        with pytest.raises(LLMError) as exc_info:
            client.chat([ChatMessage(role="user", content="Hello")])
        assert "timeout" in str(exc_info.value).lower()

    def test_set_temperature(self):
        client = OpenAIClient(api_key="test-key", temperature=0.5)
        assert client.temperature == 0.5
        client.set_temperature(0.9)
        assert client.temperature == 0.9

    def test_set_max_tokens(self):
        client = OpenAIClient(api_key="test-key", max_tokens=1000)
        assert client.max_tokens == 1000
        client.set_max_tokens(2000)
        assert client.max_tokens == 2000


class TestAnthropicClient:
    """Anthropic 客户端测试"""

    def test_client_initialization(self):
        client = AnthropicClient(
            api_key="test-key",
            model="claude-3-5-sonnet-20241022",
        )
        assert client.api_key == "test-key"
        assert client.model == "claude-3-5-sonnet-20241022"

    def test_client_without_api_key(self):
        """测试不提供 API key 时的行为"""
        client = AnthropicClient(api_key="")
        with pytest.raises(LLMError):
            client.chat([ChatMessage(role="user", content="Hello")])
