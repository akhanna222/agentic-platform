"""
LLM integration for the agentic platform
Supports OpenAI, Azure OpenAI, and AWS Bedrock
"""

import base64
import json
import threading
from typing import Any, Optional

import tiktoken
from loguru import logger
from openai import AzureOpenAI, OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_config
from app.exceptions import LLMError, TokenLimitExceeded
from app.schema import Message, ToolDefinition


class TokenCounter:
    """Token counting utility"""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_text_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def count_image_tokens(self, image_url: str, detail: str = "auto") -> int:
        """
        Count tokens for an image
        Based on OpenAI's image token calculation
        """
        if detail == "low":
            return 85

        # For high detail, we estimate based on image size
        # This is a simplified version
        return 765  # Average for high detail images

    def count_message_tokens(self, message: Message) -> int:
        """Count tokens in a message"""
        tokens = 4  # Base tokens per message

        if message.content:
            tokens += self.count_text_tokens(message.content)

        if message.images:
            for _ in message.images:
                tokens += self.count_image_tokens("", detail="high")

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tokens += self.count_text_tokens(tool_call.function.name)
                tokens += self.count_text_tokens(tool_call.function.arguments)

        return tokens

    def count_messages_tokens(self, messages: list[Message]) -> int:
        """Count total tokens in a list of messages"""
        return sum(self.count_message_tokens(msg) for msg in messages)


class LLM:
    """LLM client with support for multiple providers"""

    _instance: Optional["LLM"] = None
    _lock = threading.Lock()
    _initialized = False

    # Models that support multimodal input
    MULTIMODAL_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4-vision-preview",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
    ]

    # Reasoning models that use max_completion_tokens
    REASONING_MODELS = ["o1", "o1-mini", "o1-preview"]

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if LLM._initialized:
            return

        with LLM._lock:
            if LLM._initialized:
                return

            self.config = get_config().llm
            self.token_counter = TokenCounter(self.config.model)
            self.total_tokens = 0

            # Initialize appropriate client
            if self.config.api_type == "azure":
                self.client = AzureOpenAI(
                    api_key=self.config.api_key,
                    api_version=self.config.api_version or "2024-02-01",
                    azure_endpoint=self.config.api_base,
                    azure_deployment=self.config.azure_deployment,
                )
            elif self.config.api_type == "bedrock":
                # AWS Bedrock integration will be handled separately
                self.client = None
            else:
                # Default to OpenAI
                self.client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.api_base,
                )

            LLM._initialized = True
            logger.info(
                f"LLM initialized with model: {self.config.model}, type: {self.config.api_type}"
            )

    def _check_token_limit(self, messages: list[Message]) -> None:
        """Check if messages exceed token limit"""
        token_count = self.token_counter.count_messages_tokens(messages)
        if token_count > self.config.max_tokens:
            raise TokenLimitExceeded(
                f"Token count {token_count} exceeds limit {self.config.max_tokens}"
            )

    def _prepare_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """Prepare messages for API call"""
        prepared = []
        for msg in messages:
            msg_dict: dict[str, Any] = {"role": msg.role.value}

            # Handle content
            if msg.content:
                if msg.images and self._supports_vision():
                    # Multimodal message
                    content = [{"type": "text", "text": msg.content}]
                    for image in msg.images:
                        if image.startswith("data:"):
                            # Base64 encoded image
                            content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image, "detail": "high"},
                                }
                            )
                        else:
                            # URL
                            content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image, "detail": "high"},
                                }
                            )
                    msg_dict["content"] = content
                else:
                    msg_dict["content"] = msg.content

            # Handle tool calls
            if msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]

            # Handle tool response
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
                msg_dict["name"] = msg.name

            prepared.append(msg_dict)

        return prepared

    def _supports_vision(self) -> bool:
        """Check if current model supports vision"""
        return any(model in self.config.model for model in self.MULTIMODAL_MODELS)

    def _is_reasoning_model(self) -> bool:
        """Check if current model is a reasoning model"""
        return any(model in self.config.model for model in self.REASONING_MODELS)

    @retry(
        retry=retry_if_exception_type((LLMError,)),
        stop=stop_after_attempt(6),
        wait=wait_exponential(multiplier=1, min=2, max=60),
    )
    def ask(
        self,
        messages: list[Message],
        tools: Optional[list[ToolDefinition]] = None,
        tool_choice: Optional[str] = None,
        stream: bool = False,
    ) -> Message:
        """
        Send messages to LLM and get response

        Args:
            messages: List of messages
            tools: Optional list of tool definitions
            tool_choice: Tool selection strategy (auto, none, required)
            stream: Whether to stream the response

        Returns:
            Assistant message with response
        """
        try:
            self._check_token_limit(messages)
            prepared_messages = self._prepare_messages(messages)

            # Prepare API call parameters
            params: dict[str, Any] = {
                "model": self.config.model,
                "messages": prepared_messages,
                "temperature": self.config.temperature,
            }

            # Handle token limits based on model type
            if self._is_reasoning_model():
                if self.config.max_completion_tokens:
                    params["max_completion_tokens"] = self.config.max_completion_tokens
            else:
                params["max_tokens"] = self.config.max_tokens

            # Add tools if provided and not a reasoning model
            if tools and not self._is_reasoning_model():
                params["tools"] = [
                    {"type": t.type, "function": t.function} for t in tools
                ]
                if tool_choice:
                    params["tool_choice"] = tool_choice

            if stream:
                params["stream"] = True

            # Make API call
            if self.config.api_type == "bedrock":
                return self._ask_bedrock(params)
            else:
                response = self.client.chat.completions.create(**params)

            # Track token usage
            if hasattr(response, "usage"):
                self.total_tokens += response.usage.total_tokens
                logger.debug(
                    f"Token usage: {response.usage.total_tokens} (total: {self.total_tokens})"
                )

            # Extract response
            choice = response.choices[0]
            message = choice.message

            # Build response message
            response_msg = Message(role="assistant")
            if message.content:
                response_msg.content = message.content
            if hasattr(message, "tool_calls") and message.tool_calls:
                from app.schema import Function, ToolCall

                response_msg.tool_calls = [
                    ToolCall(
                        id=tc.id,
                        type=tc.type,
                        function=Function(
                            name=tc.function.name, arguments=tc.function.arguments
                        ),
                    )
                    for tc in message.tool_calls
                ]

            return response_msg

        except TokenLimitExceeded:
            raise
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            raise LLMError(f"Failed to get LLM response: {str(e)}") from e

    def _ask_bedrock(self, params: dict[str, Any]) -> Message:
        """Call AWS Bedrock API"""
        try:
            import boto3

            bedrock = boto3.client(
                "bedrock-runtime",
                region_name=self.config.aws_region,
                aws_access_key_id=self.config.aws_access_key_id,
                aws_secret_access_key=self.config.aws_secret_access_key,
            )

            # Convert to Bedrock format
            messages = params["messages"]
            model_id = params["model"]

            # Bedrock uses a different request format
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": params.get("max_tokens", 4096),
                "temperature": params.get("temperature", 0.7),
                "messages": messages,
            }

            response = bedrock.invoke_model(
                modelId=model_id, body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())

            # Convert Bedrock response to Message
            content = response_body.get("content", [{}])[0].get("text", "")
            return Message(role="assistant", content=content)

        except Exception as e:
            logger.error(f"Bedrock error: {str(e)}")
            raise LLMError(f"Bedrock API failed: {str(e)}") from e

    def get_token_count(self) -> int:
        """Get total token usage"""
        return self.total_tokens

    def reset_token_count(self) -> None:
        """Reset token counter"""
        self.total_tokens = 0


def get_llm() -> LLM:
    """Get or create global LLM instance"""
    return LLM()
