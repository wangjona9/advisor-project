"""Provider adapter: OpenAI/OpenAI-compatible, Ollama, or mock."""
from __future__ import annotations
import os
import requests


def _openai_answer(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base_url = os.getenv("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
    model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.responses.create(
        model=model,
        instructions=system_prompt,
        input=user_prompt,
    )
    return response.output_text, model


def _ollama_answer(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    r = requests.post(f"{base}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"], model


def _mock_answer(system_prompt: str, user_prompt: str) -> tuple[str, str]:
    # Deliberately simple: lets the UI/retrieval/logging pipeline be tested without any model.
    return (
        "MOCK MODE: No LLM call was made. Inspect the retrieved passages below and switch "
        "LLM_BACKEND to 'openai' or 'ollama' when a model endpoint is available.",
        "mock",
    )


def answer(system_prompt: str, user_prompt: str) -> tuple[str, str, str]:
    backend = os.getenv("LLM_BACKEND", "mock").strip().lower()
    if backend == "openai":
        text, model = _openai_answer(system_prompt, user_prompt)
    elif backend == "ollama":
        text, model = _ollama_answer(system_prompt, user_prompt)
    elif backend == "mock":
        text, model = _mock_answer(system_prompt, user_prompt)
    else:
        raise ValueError(f"Unknown LLM_BACKEND: {backend}")
    return text, backend, model
