from __future__ import annotations

"""
Central configuration for STK-MCP.

Values can be overridden via environment variables prefixed with `STK_MCP_`.
For example: `STK_MCP_DEFAULT_PORT=9000`.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class StkConfig(BaseSettings):
    """STK-MCP configuration.

    Environment variables use the `STK_MCP_` prefix, e.g., `STK_MCP_DEFAULT_PORT`.
    """

    # Physical constants / domain
    earth_radius_km: float = 6378.137

    # Scenario defaults
    default_scenario_name: str = "MCP_STK_Scenario"
    default_start_time: str = "20 Jan 2020 17:00:00.000"
    default_duration_hours: float = 48.0

    # Server defaults
    default_host: str = "127.0.0.1"
    default_port: int = 8765

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_prefix="STK_MCP_",
        extra="ignore",
    )


def get_config() -> StkConfig:
    """Return a cached settings instance."""
    # pydantic-settings already caches by default, but we can wrap for clarity
    return StkConfig()  # type: ignore[call-arg]

