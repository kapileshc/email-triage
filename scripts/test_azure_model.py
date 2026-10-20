"""Live smoke test for the Azure OpenAI v1 deployment.

Usage:
    python scripts/test_azure_model.py

Requires .env values:
    AZURE_MODEL_ENDPOINT=https://kapilesh1-2109-resource.services.ai.azure.com/openai/v1
    AZURE_MODEL_API_KEY=<your-api-key>
    AZURE_MODEL_NAME=gpt-4.1-mini
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import AuthenticationError

from app.llm.azure_foundry import generate_text


def main() -> None:
    try:
        result = generate_text(
            "You are a concise assistant.",
            "Reply with exactly: API WORKING",
            temperature=0.0,
            max_tokens=20,
        )
    except AuthenticationError as exc:
        raise SystemExit(
            "Azure rejected AZURE_MODEL_API_KEY. Copy a current key from the same "
            "Azure AI resource configured by AZURE_MODEL_ENDPOINT."
        ) from exc
    print(result)
    if result.strip() != "API WORKING":
        raise SystemExit(f"Unexpected model response: {result!r}")
    print("Azure gpt-4.1-mini smoke test passed.")


if __name__ == "__main__":
    main()
