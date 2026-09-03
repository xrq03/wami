from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import urllib.error
import urllib.request


@dataclass
class LLMConfig:
    provider: str = "openai_compatible"
    model: str = ""
    base_url: str = ""
    api_key: str = ""
    temperature: float = 0.0
    max_tokens: int = 1024
    timeout: int = 120

    @classmethod
    def from_file(cls, path: str | Path) -> "LLMConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return cls(**{key: value for key, value in data.items() if key in cls.__annotations__})

    def resolved(self) -> "LLMConfig":
        return LLMConfig(
            provider=self.provider,
            model=self.model or os.getenv("WAMI_LLM_MODEL", ""),
            base_url=(self.base_url or os.getenv("WAMI_LLM_BASE_URL", "")).rstrip("/"),
            api_key=self.api_key or os.getenv("WAMI_LLM_API_KEY", ""),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
        )


class OpenAICompatibleClient:
    """Minimal OpenAI-compatible chat-completions client.

    This avoids forcing a specific SDK. It works with OpenAI-compatible servers
    that expose `{base_url}/chat/completions`.
    """

    def __init__(self, config: LLMConfig):
        self.config = config.resolved()
        if self.config.provider != "openai_compatible":
            raise ValueError(f"Unsupported provider: {self.config.provider}")

    def chat(self, messages: list[dict]) -> str:
        if not self.config.api_key:
            raise RuntimeError(
                "LLM api_key is empty. Fill config/llm_agent.example.json or set WAMI_LLM_API_KEY."
            )
        if not self.config.base_url:
            raise RuntimeError(
                "LLM base_url is empty. Fill config/llm_agent.example.json or set WAMI_LLM_BASE_URL."
            )
        if not self.config.model:
            raise RuntimeError(
                "LLM model is empty. Fill config/llm_agent.example.json or set WAMI_LLM_MODEL."
            )
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.config.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM HTTP error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM request failed: {exc}") from exc
        return body["choices"][0]["message"]["content"]
