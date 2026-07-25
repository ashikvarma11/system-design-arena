from groq import Groq

from app.config import get_settings

_GROQ_MODEL = "llama-3.3-70b-versatile"


class LLMClient:
    """Provider-agnostic chat-completion wrapper. Week 1: Groq only.
    Week 2 adds Cerebras/Gemini fallback behind this same interface."""

    def __init__(self) -> None:
        settings = get_settings()
        self._groq = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    def complete(self, system_prompt: str, user_prompt: str, *, json_mode: bool = False) -> str:
        if self._groq is None:
            raise RuntimeError("GROQ_API_KEY is not configured")

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


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
