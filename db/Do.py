from pydantic import BaseModel
from db import SQLiteDB
import os
from typing import Optional

we_library = SQLiteDB.SQLiteDB(os.path.join('db', 'we_library.db'))


# pydantic基类
class BaseReq(BaseModel):
    class Config:
        extra = 'allow'  # 允许额外的字段


class VideoSource(BaseModel):
    table_name: str = "video_source"
    id: Optional[int] = None
    video_name: Optional[str] = None
    web_path: Optional[str] = None
    local_path: Optional[str] = None
    duration: Optional[float] = None
    duration_hms: Optional[str] = None
    description: Optional[str] = None
    video_type: Optional[bool] = 0


class AudioSource(BaseModel):
    table_name: str = "audio_source"
    id: Optional[int] = None
    audio_name: Optional[str] = None
    prompt_text: Optional[str] = None
    web_path: Optional[str] = None
    seed: Optional[int] = None
    speed: Optional[float] = None
    top_p: Optional[float] = None
    temperature: Optional[float] = None
    repetition_penalty: Optional[float] = None