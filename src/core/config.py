import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth


BASE_DIR = Path(__file__).parent.parent.parent
UPLOAD_DIR = BASE_DIR / "upload"

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

REDIRECT_URI = "http://localhost:8000/auth/yandex"

templates = Jinja2Templates(directory=TEMPLATES_DIR)

COOKIE_NAME = "bonds_audiofile"


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
    )


class SettingConn(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int

    SECRET_KEY: str
    CLIENT_ID: str
    CLIENT_SECRET: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


setting_conn = SettingConn()


class DbSetting(BaseSettings):
    url: str = (
        f"postgresql+asyncpg://"
        f"{setting_conn.postgres_user}:{setting_conn.postgres_password}"
        f"@{setting_conn.postgres_host}:{setting_conn.postgres_port}"
        f"/{setting_conn.postgres_db}"
    )
    echo: bool = False


class AuthJWT(BaseModel):
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7


class Setting(BaseSettings):
    db: DbSetting = DbSetting()
    auth_jwt: AuthJWT = AuthJWT()


setting = Setting()

oauth_yandex = OAuth()

oauth_yandex.register(
    name="yandex",
    client_id=setting_conn.CLIENT_ID,
    client_secret=setting_conn.CLIENT_SECRET,
    authorize_url="https://oauth.yandex.ru/authorize",
    access_token_url="https://oauth.yandex.ru/token",
    userinfo_endpoint="https://login.yandex.ru/info",
    client_kwargs={
        "scope": "login:email login:info",
        "token_endpoint_auth_method": "client_secret_post",
    },
)
