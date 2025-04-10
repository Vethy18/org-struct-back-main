from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StructReaderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OSB_STRUCT_READER_")
    csv_path: str = Field(default="")
