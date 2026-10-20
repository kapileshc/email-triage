from types import SimpleNamespace

import app.llm.azure_foundry as azure_foundry


def test_generate_text_uses_gpt4o_mini_and_returns_content(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="API WORKING")
                    )
                ]
            )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions())
    )

    monkeypatch.setattr(azure_foundry, "_client", lambda: fake_client)
    monkeypatch.setattr(azure_foundry.settings, "azure_model_name", "gpt-4o-mini")
    monkeypatch.setattr(azure_foundry.settings, "azure_model_max_tokens", 20)

    result = azure_foundry.generate_text(
        "You are a concise assistant.",
        "Reply with exactly: API WORKING",
        temperature=0.0,
        max_tokens=20,
    )

    assert result == "API WORKING"
    assert captured["model"] == "gpt-4o-mini"
    assert captured["temperature"] == 0.0
    assert captured["max_tokens"] == 20
    assert captured["messages"] == [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Reply with exactly: API WORKING"},
    ]
