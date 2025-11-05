"""
Ollama Client Service

Handles all interactions with the local Ollama LLM server.
Provides methods for chat completion, streaming, embeddings, and model management.

Port: 11434 (Ollama default)
Models: qwen2.5:3b (primary), mistral:latest (fallback)
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional, Any
import httpx
from pydantic import BaseModel, Field

from config.settings import settings

logger = logging.getLogger(__name__)


# Pydantic Models for Ollama API
class OllamaMessage(BaseModel):
    """Message in conversation history."""
    role: str = Field(..., description="Role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class OllamaChatRequest(BaseModel):
    """Request for chat completion."""
    model: str = Field(default=settings.ollama_default_model, description="Model name")
    messages: List[OllamaMessage] = Field(..., description="Conversation history")
    stream: bool = Field(default=False, description="Stream response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens to generate")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Nucleus sampling")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Additional model options")


class OllamaEmbeddingRequest(BaseModel):
    """Request for text embeddings."""
    model: str = Field(default=settings.ollama_default_model, description="Model name")
    prompt: str = Field(..., description="Text to embed")


class OllamaClient:
    """
    Client for interacting with local Ollama LLM server.

    Features:
    - Chat completion (streaming and non-streaming)
    - Text embeddings generation
    - Model management (list, pull, delete)
    - Conversation history management
    - Error handling with automatic fallback
    - Health checking

    Usage:
        client = OllamaClient()
        response = await client.chat("Tell me about sci-fi movies")
        async for chunk in client.stream_chat("Recommend a movie"):
            print(chunk)
    """

    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        default_model: str = settings.ollama_default_model,
        timeout: float = 120.0
    ):
        """
        Initialize Ollama client.

        Args:
            base_url (str): Ollama server URL (default: http://localhost:11434)
            default_model (str): Default model to use (default: qwen2.5:3b)
            timeout (float): Request timeout in seconds (default: 120s)
        """
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

        # Fallback models in priority order
        self.fallback_models = [
            "qwen2.5:3b",
            "mistral:latest",
            "llama2:latest",
            "incept5/llama3.1-claude:latest"
        ]

        logger.info(f"🤖 OllamaClient initialized: {self.base_url} (model: {self.default_model})")


    async def health_check(self) -> bool:
        """
        Check if Ollama server is running and responsive.

        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Ollama health check failed: {e}")
            return False


    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List all available models on the Ollama server.

        Returns:
            List[Dict]: List of model metadata
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"❌ Failed to list models: {e}")
            return []


    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama library.

        Args:
            model_name (str): Name of model to pull (e.g., "qwen2.5:3b")

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"📥 Pulling model: {model_name}")
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            )
            response.raise_for_status()
            logger.info(f"✅ Model pulled successfully: {model_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to pull model {model_name}: {e}")
            return False


    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[OllamaMessage]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Optional[str]:
        """
        Send a chat message and get response (non-streaming).

        Args:
            user_message (str): User's message
            system_prompt (str, optional): System prompt to set context
            conversation_history (List[OllamaMessage], optional): Previous messages
            model (str, optional): Model to use (defaults to self.default_model)
            temperature (float): Sampling temperature (0.0-2.0)
            max_tokens (int, optional): Max tokens to generate

        Returns:
            str: Assistant's response, or None if failed
        """
        model = model or self.default_model

        # Build messages list
        messages = []
        if system_prompt:
            messages.append(OllamaMessage(role="system", content=system_prompt))
        if conversation_history:
            messages.extend(conversation_history)
        messages.append(OllamaMessage(role="user", content=user_message))

        try:
            request_data = {
                "model": model,
                "messages": [msg.model_dump() for msg in messages],
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            if max_tokens:
                request_data["options"]["num_predict"] = max_tokens

            logger.info(f"💬 Sending chat request to {model}")
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=request_data
            )
            response.raise_for_status()

            data = response.json()
            assistant_message = data.get("message", {}).get("content", "")

            logger.info(f"✅ Received response ({len(assistant_message)} chars)")
            return assistant_message

        except Exception as e:
            logger.error(f"❌ Chat request failed: {e}")

            # Try fallback models
            if model == self.default_model:
                for fallback in self.fallback_models:
                    if fallback != model:
                        logger.warning(f"🔄 Trying fallback model: {fallback}")
                        result = await self.chat(
                            user_message=user_message,
                            system_prompt=system_prompt,
                            conversation_history=conversation_history,
                            model=fallback,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        if result:
                            return result

            return None


    async def stream_chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[OllamaMessage]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        Send a chat message and stream response chunks.

        Args:
            user_message (str): User's message
            system_prompt (str, optional): System prompt to set context
            conversation_history (List[OllamaMessage], optional): Previous messages
            model (str, optional): Model to use (defaults to self.default_model)
            temperature (float): Sampling temperature (0.0-2.0)
            max_tokens (int, optional): Max tokens to generate

        Yields:
            str: Response chunks as they arrive
        """
        model = model or self.default_model

        # Build messages list
        messages = []
        if system_prompt:
            messages.append(OllamaMessage(role="system", content=system_prompt))
        if conversation_history:
            messages.extend(conversation_history)
        messages.append(OllamaMessage(role="user", content=user_message))

        try:
            request_data = {
                "model": model,
                "messages": [msg.model_dump() for msg in messages],
                "stream": True,
                "options": {
                    "temperature": temperature,
                }
            }

            if max_tokens:
                request_data["options"]["num_predict"] = max_tokens

            logger.info(f"💬 Sending streaming chat request to {model}")

            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=request_data
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            if "message" in chunk_data:
                                content = chunk_data["message"].get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️  Failed to parse chunk: {line}")
                            continue

            logger.info("✅ Streaming completed")

        except Exception as e:
            logger.error(f"❌ Streaming chat failed: {e}")
            yield f"[Error: {str(e)}]"


    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> Optional[List[float]]:
        """
        Generate embeddings for text.

        Args:
            text (str): Text to embed
            model (str, optional): Model to use (defaults to self.default_model)

        Returns:
            List[float]: Embedding vector, or None if failed
        """
        model = model or self.default_model

        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                }
            )
            response.raise_for_status()

            data = response.json()
            embedding = data.get("embedding", [])

            logger.info(f"✅ Generated embedding (dim: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            return None


    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in parallel.

        Args:
            texts (List[str]): Texts to embed
            model (str, optional): Model to use

        Returns:
            List[Optional[List[float]]]: List of embedding vectors
        """
        tasks = [self.generate_embedding(text, model) for text in texts]
        return await asyncio.gather(*tasks)


    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("🔌 OllamaClient closed")


    async def __aenter__(self):
        """Async context manager entry."""
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global client instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """
    Get or create global Ollama client instance.

    Returns:
        OllamaClient: Global client instance
    """
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


async def shutdown_ollama_client():
    """Shutdown global Ollama client."""
    global _ollama_client
    if _ollama_client:
        await _ollama_client.close()
        _ollama_client = None
