from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    user_upload_limit = 50 * 1024 * 1024
    prem_upload_limit = 100 * 1024 * 1024


settings = Settings()
