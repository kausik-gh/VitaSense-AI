import logging
import os
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class GrokClient:
    BASE_URL = "https://api.x.ai/v1"
    DEFAULT_MODEL = "grok-3-mini"
    COMPLEX_MODEL = "grok-3"
    TIMEOUT_SECONDS = 30.0

    def __init__(self) -> None:
        load_dotenv()
        api_key = os.environ.get("GROK_API_KEY")
        if not api_key:
            raise RuntimeError("GROK_API_KEY environment variable is not set")

        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
            timeout=self.TIMEOUT_SECONDS,
        )
        self._verified_models: list[str] = []

    @property
    def verified_models(self) -> list[str]:
        return list(self._verified_models)

    async def verify_models(self) -> list[str]:
        try:
            response = await self._client.models.list()
        except Exception as exc:
            logger.error("Grok model verification request failed")
            raise RuntimeError("Grok model verification failed") from exc

        self._verified_models = [model.id for model in response.data]
        if self.DEFAULT_MODEL not in self._verified_models:
            raise RuntimeError(
                f"Model '{self.DEFAULT_MODEL}' not available. "
                f"Available models: {self._verified_models}"
            )

        logger.info("Grok model verification succeeded")
        return self.verified_models

    def _normalize_role(self, role: str) -> str:
        role_map = {"model": "assistant", "bot": "assistant", "ai": "assistant"}
        return role_map.get(role.lower(), role.lower())

    def _normalize_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [
            {
                "role": self._normalize_role(str(message["role"])),
                "content": str(message["content"]),
            }
            for message in messages
        ]

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 600,
        stream: bool = True,
    ) -> Any:
        selected_model = model or self.DEFAULT_MODEL
        if self._verified_models and selected_model not in self._verified_models:
            logger.warning("Requested Grok model unavailable; falling back to default")
            selected_model = self.DEFAULT_MODEL

        normalized_messages = self._normalize_messages(messages)

        try:
            response = await self._client.chat.completions.create(
                model=selected_model,
                messages=normalized_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
            )
        except Exception:
            logger.error("Grok chat completion request failed")
            raise

        if stream:
            return response
        return response.choices[0].message.content

    async def health_check(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            logger.error("Grok health check failed")
            return False

    async def close(self) -> None:
        close = getattr(self._client, "close", None)
        if close is None:
            return
        try:
            result = close()
            if hasattr(result, "__await__"):
                await result
        except Exception:
            logger.error("Grok client close failed")
