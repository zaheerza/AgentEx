"""
LLM Provider abstraction layer for multi-provider support.

This allows switching between Anthropic, Groq, OpenAI, etc. without
changing agent code.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def create_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        system: Optional[str] = None
    ) -> Any:
        """Create a completion with the LLM"""
        pass

    @abstractmethod
    def get_stop_reason(self, response: Any) -> str:
        """Get the stop reason from response"""
        pass

    @abstractmethod
    def get_content(self, response: Any) -> List[Any]:
        """Get content blocks from response"""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) provider"""

    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def create_completion(self, model, messages, tools=None, max_tokens=4096, system=None):
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        if tools:
            kwargs["tools"] = tools
        if system:
            kwargs["system"] = system

        return self.client.messages.create(**kwargs)

    def get_stop_reason(self, response):
        return response.stop_reason

    def get_content(self, response):
        return response.content


class GroqProvider(LLMProvider):
    """Groq provider using OpenAI-compatible API"""

    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )

    def create_completion(self, model, messages, tools=None, max_tokens=4096, system=None):
        # Convert Anthropic-style messages to OpenAI format
        openai_messages = self._convert_messages(messages, system)

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": openai_messages
        }
        if tools:
            kwargs["tools"] = self._convert_tools(tools)

        return self.client.chat.completions.create(**kwargs)

    def _convert_messages(self, messages, system=None):
        """Convert Anthropic format to OpenAI format"""
        openai_messages = []

        if system:
            openai_messages.append({"role": "system", "content": system})

        for msg in messages:
            openai_messages.append({
                "role": msg["role"],
                "content": self._extract_content(msg["content"])
            })

        return openai_messages

    def _extract_content(self, content):
        """Extract text content from Anthropic format"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Extract text from content blocks
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block["text"])
                elif hasattr(block, "text"):
                    text_parts.append(block.text)
            return " ".join(text_parts) if text_parts else ""
        return str(content)

    def _convert_tools(self, tools):
        """Convert Anthropic tool format to OpenAI format"""
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return openai_tools

    def get_stop_reason(self, response):
        finish_reason = response.choices[0].finish_reason
        # Map OpenAI finish reasons to Anthropic-style
        mapping = {
            "stop": "end_turn",
            "tool_calls": "tool_use",
            "length": "max_tokens"
        }
        return mapping.get(finish_reason, finish_reason)

    def get_content(self, response):
        """Convert OpenAI response to Anthropic-style content blocks"""
        choice = response.choices[0]
        content_blocks = []

        # Text content
        if choice.message.content:
            content_blocks.append(
                type("ContentBlock", (), {
                    "type": "text",
                    "text": choice.message.content
                })()
            )

        # Tool calls
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                import json
                content_blocks.append(
                    type("ToolUse", (), {
                        "type": "tool_use",
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "input": json.loads(tool_call.function.arguments)
                    })()
                )

        return content_blocks


class OpenAIProvider(LLMProvider):
    """OpenAI (GPT) provider"""

    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def create_completion(self, model, messages, tools=None, max_tokens=4096, system=None):
        # Similar to GroqProvider
        openai_messages = []
        if system:
            openai_messages.append({"role": "system", "content": system})

        for msg in messages:
            openai_messages.append({"role": msg["role"], "content": str(msg["content"])})

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": openai_messages
        }
        if tools:
            kwargs["tools"] = tools

        return self.client.chat.completions.create(**kwargs)

    def get_stop_reason(self, response):
        finish_reason = response.choices[0].finish_reason
        mapping = {"stop": "end_turn", "tool_calls": "tool_use"}
        return mapping.get(finish_reason, finish_reason)

    def get_content(self, response):
        # Similar to GroqProvider
        choice = response.choices[0]
        content_blocks = []
        if choice.message.content:
            content_blocks.append(
                type("ContentBlock", (), {"type": "text", "text": choice.message.content})()
            )
        return content_blocks


def get_provider(provider_name: str, api_key: str) -> LLMProvider:
    """
    Factory function to get the appropriate provider.

    Args:
        provider_name: Name of provider ('anthropic', 'groq', 'openai')
        api_key: API key for the provider

    Returns:
        LLMProvider instance
    """
    providers = {
        "anthropic": AnthropicProvider,
        "groq": GroqProvider,
        "openai": OpenAIProvider
    }

    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")

    return provider_class(api_key)
