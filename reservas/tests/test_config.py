from app.config import Settings, settings


def test_settings_cargan_desde_entorno():
    assert settings.SECRET_KEY is not None
    assert len(settings.SECRET_KEY) >= 32
    assert settings.DATABASE_URL.startswith("sqlite")
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
    assert settings.ALGORITHM == "HS256"


def test_settings_propiedades_compatibilidad():
    assert settings.secret_key == settings.SECRET_KEY
    assert settings.database_url == settings.DATABASE_URL
    assert settings.access_token_expire_minutes == settings.ACCESS_TOKEN_EXPIRE_MINUTES


def test_settings_instancia_personalizada():
    custom = Settings(
        SECRET_KEY="otra_clave_muy_segura_de_prueba_1234567890",
        DATABASE_URL="sqlite:///:memory:",
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
    )
    assert custom.SECRET_KEY == "otra_clave_muy_segura_de_prueba_1234567890"
    assert custom.DATABASE_URL == "sqlite:///:memory:"
    assert custom.ACCESS_TOKEN_EXPIRE_MINUTES == 15
