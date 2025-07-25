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
    local_path: Optional[str] = None


def test_nltk():
    # 问题：语音克隆英文转换报错
    import nltk
    # nltk.download("punkt_tab")
    # nltk.download('averaged_perceptron_tagger_eng')
    # 直接下载网络太慢
    # 手动下载（需要手动解压 win地址：C:\Users\1\AppData\Roaming\nltk_data）
    # https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/taggers/averaged_perceptron_tagger_eng.zip
    # https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip

    sample_text = "This is a test sentence."
    tokens = nltk.word_tokenize(sample_text)
    tags = nltk.pos_tag(tokens)
    print("NLTK配置成功！")
    print("词性标注结果:", tags)


if __name__ == '__main__':
    test_nltk()
