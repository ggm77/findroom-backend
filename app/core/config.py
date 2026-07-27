from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FINDROOM_", env_file=".env")

    timetable_xls_path: Path = Path("/Users/user/Downloads/개설시간표.xls")
    timetable_encoding: str = "cp949"


settings = Settings()
