"""
Environment Configuration Manager
Handles environment detection and configuration for staging/production deployments.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EnvironmentConfig:
    """Configuration for different environments."""
    name: str
    is_production: bool
    is_staging: bool
    is_development: bool
    debug: bool
    allowed_origins: list[str]
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    cache_ttl: int
    log_level: str
    enable_experimental: bool
    enable_debug_endpoints: bool
    session_timeout_minutes: int
    cost_budget_monthly: float
    cost_alert_threshold: float


class EnvironmentManager:
    """Manages environment configuration and detection."""

    def __init__(self):
        self.env_name = os.getenv("ENVIRONMENT", "development")
        self._config = self._load_config()

    def _load_config(self) -> EnvironmentConfig:
        """Load configuration based on environment."""

        # Determine environment
        is_production = self.env_name == "production"
        is_staging = self.env_name == "staging"
        is_development = self.env_name == "development"

        # Production configuration
        if is_production:
            return EnvironmentConfig(
                name="production",
                is_production=True,
                is_staging=False,
                is_development=False,
                debug=False,
                allowed_origins=self._get_list_env(
                    "ALLOWED_ORIGINS",
                    ["https://persona-assessment.vercel.app"]
                ),
                rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "30")),
                rate_limit_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "300")),
                cache_ttl=int(os.getenv("CACHE_TTL_SECONDS", "600")),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                enable_experimental=self._get_bool_env("ENABLE_EXPERIMENTAL_FEATURES", False),
                enable_debug_endpoints=False,
                session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "30")),
                cost_budget_monthly=float(os.getenv("MONTHLY_COST_BUDGET", "200")),
                cost_alert_threshold=float(os.getenv("COST_ALERT_THRESHOLD", "0.9")),
            )

        # Staging configuration
        elif is_staging:
            return EnvironmentConfig(
                name="staging",
                is_production=False,
                is_staging=True,
                is_development=False,
                debug=True,
                allowed_origins=self._get_list_env(
                    "ALLOWED_ORIGINS",
                    [
                        "https://persona-assessment-staging.vercel.app",
                        "http://localhost:3000"
                    ]
                ),
                rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
                rate_limit_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000")),
                cache_ttl=int(os.getenv("CACHE_TTL_SECONDS", "300")),
                log_level=os.getenv("LOG_LEVEL", "DEBUG"),
                enable_experimental=self._get_bool_env("ENABLE_EXPERIMENTAL_FEATURES", True),
                enable_debug_endpoints=True,
                session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "60")),
                cost_budget_monthly=float(os.getenv("MONTHLY_COST_BUDGET", "50")),
                cost_alert_threshold=float(os.getenv("COST_ALERT_THRESHOLD", "0.8")),
            )

        # Development configuration
        else:
            return EnvironmentConfig(
                name="development",
                is_production=False,
                is_staging=False,
                is_development=True,
                debug=True,
                allowed_origins=self._get_list_env(
                    "ALLOWED_ORIGINS",
                    ["*"]
                ),
                rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000")),
                rate_limit_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "10000")),
                cache_ttl=int(os.getenv("CACHE_TTL_SECONDS", "60")),
                log_level=os.getenv("LOG_LEVEL", "DEBUG"),
                enable_experimental=True,
                enable_debug_endpoints=True,
                session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "120")),
                cost_budget_monthly=float(os.getenv("MONTHLY_COST_BUDGET", "10")),
                cost_alert_threshold=float(os.getenv("COST_ALERT_THRESHOLD", "0.5")),
            )

    @staticmethod
    def _get_bool_env(key: str, default: bool) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default))
        return value.lower() in ("true", "1", "yes")

    @staticmethod
    def _get_list_env(key: str, default: list[str]) -> list[str]:
        """Get list from environment variable (comma-separated)."""
        value = os.getenv(key)
        if value:
            return [item.strip() for item in value.split(",")]
        return default

    @property
    def config(self) -> EnvironmentConfig:
        """Get current environment configuration."""
        return self._config

    def is_production(self) -> bool:
        """Check if running in production."""
        return self._config.is_production

    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self._config.is_staging

    def is_development(self) -> bool:
        """Check if running in development."""
        return self._config.is_development

    def get_database_url(self) -> str:
        """Get database URL for current environment."""
        return os.getenv("DATABASE_URL", "sqlite:///./assessment.db")

    def get_api_key(self) -> Optional[str]:
        """Get API key for current environment."""
        return os.getenv("ANTHROPIC_API_KEY")

    def get_admin_password_hash(self) -> Optional[str]:
        """Get admin password hash."""
        return os.getenv("ADMIN_PASSWORD_HASH")

    def get_admin_api_key(self) -> Optional[str]:
        """Get admin API key."""
        return os.getenv("ADMIN_API_KEY")

    def get_sentry_dsn(self) -> Optional[str]:
        """Get Sentry DSN for error tracking."""
        return os.getenv("SENTRY_DSN")

    def get_info(self) -> Dict[str, Any]:
        """Get environment information."""
        config = self._config
        return {
            "environment": config.name,
            "is_production": config.is_production,
            "is_staging": config.is_staging,
            "is_development": config.is_development,
            "debug": config.debug,
            "log_level": config.log_level,
            "rate_limits": {
                "per_minute": config.rate_limit_per_minute,
                "per_hour": config.rate_limit_per_hour,
            },
            "cache_ttl": config.cache_ttl,
            "features": {
                "experimental": config.enable_experimental,
                "debug_endpoints": config.enable_debug_endpoints,
            },
            "cost_tracking": {
                "monthly_budget": config.cost_budget_monthly,
                "alert_threshold": config.cost_alert_threshold,
            },
        }

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate environment configuration.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Required environment variables
        required_vars = [
            "ANTHROPIC_API_KEY",
            "ADMIN_PASSWORD_HASH",
        ]

        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")

        # Production-specific validations
        if self.is_production():
            # Check that DEBUG is false
            if self._config.debug:
                errors.append("DEBUG should be false in production")

            # Check that experimental features are disabled
            if self._config.enable_experimental:
                errors.append("Experimental features should be disabled in production")

            # Check that debug endpoints are disabled
            if self._config.enable_debug_endpoints:
                errors.append("Debug endpoints should be disabled in production")

            # Check ALLOWED_ORIGINS is not wildcard
            if "*" in self._config.allowed_origins:
                errors.append("ALLOWED_ORIGINS should not contain wildcard in production")

        return (len(errors) == 0, errors)


# Global environment manager instance
env_manager = EnvironmentManager()


# Convenience functions
def get_environment() -> str:
    """Get current environment name."""
    return env_manager.config.name


def is_production() -> bool:
    """Check if running in production."""
    return env_manager.is_production()


def is_staging() -> bool:
    """Check if running in staging."""
    return env_manager.is_staging()


def is_development() -> bool:
    """Check if running in development."""
    return env_manager.is_development()


def get_config() -> EnvironmentConfig:
    """Get current environment configuration."""
    return env_manager.config


def validate_environment() -> tuple[bool, list[str]]:
    """Validate current environment configuration."""
    return env_manager.validate_config()


# Example usage
if __name__ == "__main__":
    import json

    print("Environment Configuration")
    print("=" * 50)
    print(json.dumps(env_manager.get_info(), indent=2))
    print()

    # Validate configuration
    is_valid, errors = validate_environment()
    if is_valid:
        print("✓ Environment configuration is valid")
    else:
        print("✗ Environment configuration has errors:")
        for error in errors:
            print(f"  - {error}")
