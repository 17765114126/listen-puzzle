from pydantic import BaseModel


# pydantic基类
class BaseReq(BaseModel):
    class Config:
        extra = 'allow'  # 允许额外的字段