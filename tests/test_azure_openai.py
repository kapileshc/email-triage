import app.llm.azure_foundry as azure_foundry


def test_generate_text_uses_responses_api_and_returns_content(monkeypatch):
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return type("Response", (), {"output_text": "API WORKING"})()

    fake_client = type("Client", (), {"responses": FakeResponses()})()

    monkeypatch.setattr(azure_foundry, "_client", lambda: fake_client)
    monkeypatch.setattr(azure_foundry.settings, "azure_model_name", "gpt-4.1-mini")
    monkeypatch.setattr(azure_foundry.settings, "azure_model_max_tokens", 20)

    result = azure_foundry.generate_text(
        "You are a concise assistant.",
        "Reply with exactly: API WORKING",
        temperature=0.0,
        max_tokens=20,
    )

    assert result == "API WORKING"
    assert captured["model"] == "gpt-4.1-mini"
    assert captured["temperature"] == 0.0
    assert captured["max_output_tokens"] == 20
    assert captured["instructions"] == "You are a concise assistant."
    assert captured["input"] == "Reply with exactly: API WORKING"
