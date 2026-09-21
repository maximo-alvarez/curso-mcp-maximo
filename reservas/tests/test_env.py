from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def test_env_example_existe_y_tiene_claves_requeridas():
    env_example = REPO_ROOT / ".env.example"
    assert env_example.exists(), "El archivo .env.example debe existir"
    content = env_example.read_text()
    for key in ["SECRET_KEY", "DATABASE_URL", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
        assert f"{key}=" in content, f"{key} debe estar definido en .env.example"

def test_env_local_existe_y_tiene_valores_validos():
    env_file = REPO_ROOT / ".env"
    assert env_file.exists(), "El archivo .env debe existir"
    content = env_file.read_text()
    lines = dict(
        line.split("=", 1)
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#") and "=" in line
    )
    assert len(lines.get("SECRET_KEY", "")) >= 32, "SECRET_KEY debe tener al menos 32 caracteres seguros"
    assert lines.get("DATABASE_URL", "").startswith("sqlite"), "DATABASE_URL debe estar configurado"
    assert int(lines.get("ACCESS_TOKEN_EXPIRE_MINUTES", "0")) > 0, "ACCESS_TOKEN_EXPIRE_MINUTES debe ser > 0"

def test_env_ignorado_en_gitignore():
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), "El archivo .gitignore debe existir"
    content = gitignore.read_text()
    assert ".env" in content, ".env debe estar en .gitignore para evitar fugas de secretos"
