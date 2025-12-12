
import logging
import os

from openai import OpenAI

log = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI | None:
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log.warning("OPENAI_API_KEY is not set; GPT replies will be disabled.")
        return None
    _client = OpenAI(api_key=api_key)
    return _client


def generate_reply(prompt: str) -> str:
    client = _get_client()
    if not client:
        return "OPENAI_API_KEY is not set. Please configure it in your environment."

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=15,
        )
        return response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001 - want full capture
        log.error("OpenAI reply failed: %s", exc)
        return "Error generating reply right now. Please try again later."
