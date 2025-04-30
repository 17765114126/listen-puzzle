from data import find_duplicates
from fastapi import APIRouter
from api.Do import BaseReq

router = APIRouter()

from typing import Optional, Any


def result(code: int = 0, data: Optional[Any] = None, msg: str = "success") -> dict:
    """统一API响应格式
    :param code: 状态码（默认0表示成功）
    :param data: 返回数据（可选）
    :param msg: 返回信息（默认'success'）
    """
    return {
        "code": code,
        "data": data,
        "msg": msg

    }


# 查找重复文件
@router.post("/find_duplicates")
async def find_repeat_file(req: BaseReq):
    folder_path = req.folder_path
    duplicates = find_duplicates.run_duplicates(folder_path)
    return result(0, duplicates)
