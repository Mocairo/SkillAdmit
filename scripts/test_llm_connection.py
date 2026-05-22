#!/usr/bin/env python3
from __future__ import annotations

import os
import time
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    load_dotenv(ROOT / ".env")

    api_key = require_env("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")
    model = os.getenv("SKILLADMIT_MODEL", "mimo-v2.5-pro")

    client = OpenAI(api_key=api_key, base_url=base_url)

    start = time.perf_counter()
    first_token_time = None
    output_text = ""
    usage = None

    stream = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are MiMo, an AI assistant developed by Xiaomi. Answer only with the final answer.",
            },
            {
                "role": "user",
                "content": "请只回复这一句话：SkillAdmit connection ok",
            },
        ],
        temperature=1.0,
        top_p=0.95,
        max_completion_tokens=256,
        stream=True,
        stream_options={"include_usage": True},
    )

    for chunk in stream:
        now = time.perf_counter()

        if getattr(chunk, "usage", None) is not None:
            usage = chunk.usage

        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta.content
        if delta:
            if first_token_time is None:
                first_token_time = now
            output_text += delta

    elapsed = time.perf_counter() - start

    print("model:", model)
    print("base_url:", base_url)
    print("reply:", output_text.strip())
    print(f"latency_seconds: {elapsed:.3f}")

    if first_token_time is not None:
        print(f"ttft_seconds: {first_token_time - start:.3f}")

    if usage is not None:
        print("prompt_tokens:", usage.prompt_tokens)
        print("completion_tokens:", usage.completion_tokens)
        print("total_tokens:", usage.total_tokens)


if __name__ == "__main__":
    main()
