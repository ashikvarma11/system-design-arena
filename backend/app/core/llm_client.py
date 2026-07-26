import logging

import httpx
from cerebras.cloud.sdk import Cerebras
from google import genai
from google.genai import types as genai_types
from groq import Groq

from app.config import get_settings

logger = logging.getLogger(__name__)

_OPENROUTER_MODEL = "deepseek/deepseek-chat-v3.1:free"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
_GROQ_MODEL = "llama-3.3-70b-versatile"
_CEREBRAS_MODEL = "llama-3.3-70b"
_GEMINI_MODEL = "gemini-2.0-flash"


class ProviderUnavailable(Exception):
    """Raised by a provider call so the client can fall back to the next one."""


class LLMClient:
    """Provider-agnostic chat-completion wrapper.

    Tries OpenRouter -> Groq -> Cerebras -> Gemini in order, falling back to
    the next provider whenever one is unconfigured, rate-limited, or errors
    out. Persona code never touches provider specifics.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._openrouter_key = settings.openrouter_api_key or None
        self._http = httpx.Client(timeout=60.0)
        self._groq = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        self._cerebras = (
            Cerebras(api_key=settings.cerebras_api_key) if settings.cerebras_api_key else None
        )
        self._gemini = (
            genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None
        )

    def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> str:
        providers = (
            ("openrouter", self._complete_openrouter),
            ("groq", self._complete_groq),
            ("cerebras", self._complete_cerebras),
            ("gemini", self._complete_gemini),
        )
        last_error: Exception | None = None
        for name, fn in providers:
            try:
                return fn(system_prompt, user_prompt, json_mode=json_mode)
            except ProviderUnavailable as exc:
                last_error = exc
                continue
            except Exception as exc:  # noqa: BLE001 - provider SDK errors vary widely
                logger.warning("LLM provider %s failed, falling back: %s", name, exc)
                last_error = exc
                continue
        raise RuntimeError(f"All LLM providers unavailable: {last_error}")

    def _complete_openrouter(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> str:
        if self._openrouter_key is None:
            raise ProviderUnavailable("OPENROUTER_API_KEY not configured")
        response = self._http.post(
            _OPENROUTER_BASE_URL,
            headers={"Authorization": f"Bearer {self._openrouter_key}"},
            json={
                "model": _OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"} if json_mode else None,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"] or ""

    def _complete_groq(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> str:
        if self._groq is None:
            raise ProviderUnavailable("GROQ_API_KEY not configured")
        response = self._groq.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"} if json_mode else None,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    def _complete_cerebras(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> str:
        if self._cerebras is None:
            raise ProviderUnavailable("CEREBRAS_API_KEY not configured")
        response = self._cerebras.chat.completions.create(
            model=_CEREBRAS_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"} if json_mode else None,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    def _complete_gemini(self, system_prompt: str, user_prompt: str, *, json_mode: bool) -> str:
        if self._gemini is None:
            raise ProviderUnavailable("GEMINI_API_KEY not configured")
        response = self._gemini.models.generate_content(
            model=_GEMINI_MODEL,
            contents=user_prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                response_mime_type="application/json" if json_mode else "text/plain",
            ),
        )
        return response.text or ""


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
