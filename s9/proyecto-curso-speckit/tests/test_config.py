import pytest
from app.config import Settings, settings


def test_settings_cargan_desde_entorno():
    assert settings.secret_key is not None
    assert len(settings.secret_key) >= 10
    assert settings.database_url.startswith("sqlite") or settings.database_url.startswith("postgresql")
    assert settings.access_token_expire_minutes == 30
    assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
    assert settings.mcp_demo_email == "demo@curso.com"


def test_settings_custom_values():
    custom = Settings(secret_key="custom_secret_key_1234567890", access_token_expire_minutes=60)
    assert custom.secret_key == "custom_secret_key_1234567890"
    assert custom.access_token_expire_minutes == 60
