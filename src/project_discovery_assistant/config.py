"""Typed application configuration."""

from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from project_discovery_assistant.errors import ConfigurationError


class Settings(BaseSettings):
    """Configuration loaded from environment variables and an optional .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )

    openai_api_key: SecretStr | None = None
    model_name: str = "gpt-4o-mini"
    openai_base_url: str | None = None
    pdpa_projects_dir: Path = Path("./projects")
    pdpa_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    def require_provider(self) -> str:
        """Return the provider key or raise a safe, actionable error."""
        if self.openai_api_key is None or not self.openai_api_key.get_secret_value():
            raise ConfigurationError(
                "Provider configuration is required for this command. "
                "Set OPENAI_API_KEY in the environment or an untracked .env file."
            )
        return self.openai_api_key.get_secret_value()

    def resolved_projects_dir(self, workspace: Path | None = None) -> Path:
        """Resolve and validate the local runtime-artifact directory."""
        resolved = self.pdpa_projects_dir.expanduser().resolve()
        if workspace is not None:
            workspace_resolved = workspace.expanduser().resolve()
            try:
                resolved.relative_to(workspace_resolved)
            except ValueError as error:
                raise ConfigurationError(
                    "PDPA_PROJECTS_DIR must resolve inside the configured workspace."
                ) from error
        return resolved
