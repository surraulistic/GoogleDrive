# SETTINGS FILE
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    user_upload_limit = 50 * 1024 * 1024
    prem_upload_limit = 100 * 1024 * 1024


user_upload_limit = Settings().user_upload_limit
prem_upload_limit = Settings().prem_upload_limit

