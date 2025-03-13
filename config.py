from dotenv import load_dotenv
from pydantic import PostgresDsn, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class InfrastructureConfig(BaseSettings):
    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int = 5432
    db_driver: str = "postgresql"
    postgres_dsn: PostgresDsn | None = None


    @field_validator("postgres_dsn", mode="after")
    @classmethod
    def get_postgres_dsn(cls, _, info: ValidationInfo):
        return PostgresDsn.build(
            username=info.data["db_user"],
            password=info.data["db_password"],
            path=info.data["db_name"],
            host=info.data["db_host"],
            port=info.data["db_port"],
            scheme=info.data["db_driver"],
        )


class ApiConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="api_")

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    WORKERS: int = 1
    ALLOWED_HOSTS: list[str] = ["*"]


class FileConfig(BaseSettings):
    user_upload_limit: int = 50 * 1024 * 1024
    prem_upload_limit: int = 100 * 1024 * 1024


file_config = FileConfig()


class Settings(BaseSettings):
    infrastructure_config: InfrastructureConfig = InfrastructureConfig()
    api_config: ApiConfig = ApiConfig()
    file_config: FileConfig = FileConfig()


settings = Settings()