import importlib
from pathlib import Path


def test_resolve_api_key_uses_project_root_env(monkeypatch, tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    env_path = project_root / ".env"
    assert env_path.exists(), "Expected a project-level .env file"

    with env_path.open("r", encoding="utf-8") as handle:
        env_contents = handle.read()

    assert "GEMINI_API_KEY=" in env_contents, "Expected GEMINI_API_KEY in .env"

    import src.llm_investigator as mod

    importlib.reload(mod)
    resolved = mod.resolve_api_key()
    assert resolved is not None
    assert resolved.startswith(("AI", "AQ.", "AIza"))
