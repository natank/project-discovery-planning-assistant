"""Tests for the typed configuration boundary."""

from pathlib import Path

import pytest
from pydantic import SecretStr, ValidationError

from project_discovery_assistant.config import Settings
from project_discovery_assistant.errors import ConfigurationError


def test_settings_load_non_secret_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODEL_NAME", "fixture-model")
    monkeypatch.setenv("PDPA_PROJECTS_DIR", "./test-projects")
    monkeypatch.setenv("PDPA_LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)

    assert settings.model_name == "fixture-model"
    assert settings.pdpa_projects_dir == Path("./test-projects")
    assert settings.pdpa_log_level == "DEBUG"


def test_provider_requirement_is_lazy_and_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings = Settings(_env_file=None)

    with pytest.raises(ConfigurationError) as error:
        settings.require_provider()

    assert "OPENAI_API_KEY" in str(error.value)
    assert "None" not in str(error.value)


def test_provider_secret_is_available_only_through_explicit_requirement() -> None:
    settings = Settings(
        _env_file=None,
        openai_api_key=SecretStr("sentinel-secret"),
    )

    assert settings.require_provider() == "sentinel-secret"
    assert "sentinel-secret" not in repr(settings)


def test_projects_dir_must_remain_inside_workspace(tmp_path: Path) -> None:
    settings = Settings(_env_file=None, pdpa_projects_dir=tmp_path / "projects")

    assert settings.resolved_projects_dir(tmp_path) == tmp_path / "projects"

    outside = Settings(_env_file=None, pdpa_projects_dir=tmp_path.parent)
    with pytest.raises(ConfigurationError):
        outside.resolved_projects_dir(tmp_path)


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, pdpa_log_level="TRACE")
