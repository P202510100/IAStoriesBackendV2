from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENAI_API_KEY: str
    FREEPIK_API_KEY: str

    model_config = ConfigDict(env_file=".env")

#    f"postgresql://postgres:{settings.DB_PASS}@db.rsjtpijgsibxsczrpcjh.supabase.co:5432/postgres"

settings = Settings()

# Construcción directa de la URI de conexión
SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
