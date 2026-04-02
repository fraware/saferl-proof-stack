"""Fireworks DeepSeek-Prover API integration for Lean proof completion."""

from collections.abc import AsyncIterator

import httpx

from .errors import ProverAPIError, ProverNetworkError
from .observability import get_logger, log_event

LOGGER = get_logger(__name__)

class ProverAPI:
    """
    Client for Fireworks DeepSeek-Prover API.
    Handles Lean proof completion via hosted model.
    """

    def __init__(self, api_key, model="fireworks/deepseek-prover-v2"):
        """Initialize the prover API client.

        Args:
            api_key: Fireworks API key
            model: Model to use for proof generation
        """
        self.url = "https://api.fireworks.ai/inference/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.model = model

    def complete(self, lean_code):
        """
        Sends Lean code to the prover and returns the completed proof.
        """
        messages = [
            {
                "role": "system",
                "content": "You are DeepSeek Prover. Produce Lean4 proofs; no natural-language.",
            },
            {"role": "user", "content": lean_code},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
            "stream": False,
            "max_tokens": 2048,
        }

        try:
            r = httpx.post(self.url, json=payload, headers=self.headers, timeout=120)
            r.raise_for_status()
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ProverAPIError("Prover response contained empty proof content.")
            return content
        except httpx.HTTPStatusError as exc:
            response_text = exc.response.text if exc.response else "no_response"
            log_event(
                LOGGER,
                "prover_api_http_error",
                status_code=exc.response.status_code if exc.response else None,
                response_text=response_text,
            )
            raise ProverAPIError(
                f"Prover API returned HTTP error: {exc}"
            ) from exc
        except httpx.HTTPError as exc:
            log_event(LOGGER, "prover_api_network_error", error=str(exc))
            raise ProverNetworkError(f"Prover API network failure: {exc}") from exc

    async def stream(self, lean_file: str) -> AsyncIterator[str]:
        """Stream proof generation updates in real-time.

        Args:
            lean_file: Path to the Lean file to prove

        Yields:
            Status updates as strings
        """
        try:
            # Read the Lean file
            with open(lean_file, encoding="utf-8") as f:
                lean_code = f.read()

            yield "🤖 Reading Lean specification..."

            # Make streaming API call
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    self.url,
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a Lean4 theorem prover. Complete the proof by replacing 'sorry' with valid Lean tactics.",
                            },
                            {"role": "user", "content": lean_code},
                        ],
                        "temperature": 0.0,
                        "stream": True,
                        "max_tokens": 2048,
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()

                    yield "🤖 Analyzing proof structure..."

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                break

                            try:
                                import json

                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        content = delta["content"]
                                        if content.strip():
                                            yield f"🤖 {content.strip()}"
                            except json.JSONDecodeError:
                                continue

                    yield "✅ Proof generation completed!"

        except Exception as exc:
            log_event(LOGGER, "prover_stream_error", error=str(exc))
            raise ProverNetworkError(f"Streaming proof generation failed: {exc}") from exc
