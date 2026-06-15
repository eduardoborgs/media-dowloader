from pydantic import BaseModel, field_validator
from typing import Optional, List


class MediaRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("A URL deve começar com http:// ou https://")
        if len(v) > 2000:
            raise ValueError("URL muito longa (máx. 2000 caracteres)")
        return v


class Format(BaseModel):
    format_id: str
    ext: str
    label: str
    filesize: Optional[int] = None
    is_audio_only: bool = False


class MediaInfo(BaseModel):
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: str
    platform: str
    formats: List[Format] = []