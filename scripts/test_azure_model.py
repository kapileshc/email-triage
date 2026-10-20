"""Live smoke test for the Azure OpenAI v1 deployment.

Usage:
    python scripts/test_azure_model.py

Requires .env values:
    AZURE_MODEL_ENDPOINT=https://emailtriage.openai.azure.com/openai/v1/
    AZURE_MODEL_API_KEY=<rotated key>
    AZURE_MODEL_NAME=gpt-4o-mini
"""

from app.llm.azure_foundry import generate_text


def main() -> None:
    result = generate_text(
        "You are a concise assistant.",
        "Reply with exactly: API WORKING",
        temperature=0.0,
        max_tokens=20,
    )
    print(result)
    if result.strip() != "API WORKING":
        raise SystemExit(f"Unexpected model response: {result!r}")
    print("Azure gpt-4o-mini smoke test passed.")


if __name__ == "__main__":
    main()
