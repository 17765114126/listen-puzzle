from pydantic import BaseModel
from db import SQLiteDB
import os
from typing import Optional

we_library = SQLiteDB.SQLiteDB(os.path.join('db', 'we_library.db'))


# pydantic基类
class BaseReq(BaseModel):
    class Config:
        extra = 'allow'  # 允许额外的字段


class ChatHistoryTitle(BaseModel):
    table_name: str = "chat_history_title"
    id: Optional[int] = None
    introduce: Optional[str] = None
    user_id: Optional[int] = None


class ChatHistory(BaseModel):
    table_name: str = "chat_history"
    id: Optional[int] = None
    thumb_img: Optional[str] = None
    content: Optional[str] = None
    chat_history_title_id: Optional[int] = None
    role_type: Optional[str] = None


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
