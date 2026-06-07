from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(Path(__file__).resolve().parents[2] / ".env"), env_ignore_empty=True, extra="ignore")

    app_name: str = "mt5-relay"
    secret_key: str = ""
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_minutes: int = 60 * 24 * 14
    database_url: str = ""

    public_web_url: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_ssl: bool = False
    smtp_starttls: bool = True
    password_reset_expire_minutes: int = 30


settings = Settings()

if not settings.database_url:
    if Path("/data").exists():
        settings.database_url = "sqlite:////data/app.db"
    else:
        settings.database_url = "sqlite:///./app.db"

if not settings.secret_key:
    if Path("/data").exists():
        p = Path("/data/secret_key")
    else:
        p = Path(__file__).resolve().parents[2] / ".secret_key"
    try:
        if p.exists():
            settings.secret_key = p.read_text(encoding="utf-8").strip()
        else:
            settings.secret_key = secrets.token_urlsafe(48)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(settings.secret_key, encoding="utf-8")
    except Exception:
        settings.secret_key = secrets.token_urlsafe(48)
