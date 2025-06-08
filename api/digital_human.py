import json
from fastapi import APIRouter

from db.Do import BaseReq, we_library, ChatHistory, ChatRole
from data import use_llm

router = APIRouter()


@router.post("/chat_list")
async def chat_list():
    # 获取记录列表
    return we_library.fetch_all("SELECT id,introduce FROM chat_history", tuple([]))


@router.get("/chat_del")
async def chat_del(id: int):
    # 删除记录列表
    we_library.execute_query("DELETE FROM chat_history WHERE id=?;", (id,))
    return True


@router.get("/chat_info")
def chat_info(id: int):
    # 根据id查询详细记录
    return we_library.fetch_one(f"SELECT id,content FROM chat_history WHERE id=?;", (id,))


@router.post("/chat")
def chat(req: BaseReq):
    req_dict = req.dict()
    messages = []
    # 初始化角色设置
    if req_dict.get("currentRole"):
        role_info = we_library.fetch_one(f"SELECT id,role_name,role_setting FROM chat_role WHERE id=?;",
                                         (req_dict.get("currentRole"),))
        system_content = f"""
        名称：{role_info.get("role_name")}，描述：{role_info.get("role_setting")}
        """
        system_messages = {"role": "system", "content": system_content}
        messages.append(system_messages)

    prompt_messages = {"role": "user", "content": req.prompt}
    # 创建 ChatHistory 实例
    chat_history = ChatHistory(
        table_name="chat_history",  # 直接初始化字段值
        introduce=req.prompt if req_dict.get("id") is None else None,
        id=req_dict.get("id")
    )
    if req_dict.get("id"):
        db_record = we_library.fetch_one("SELECT content FROM chat_history WHERE id=?", (req_dict["id"],))
        if db_record and db_record.get("content"):
            messages.extend(json.loads(db_record["content"]))
    # 添加新消息
    messages.append(prompt_messages)
    resp = use_llm._generate_response(messages)

    messages.append({"role": "assistant", "content": resp})
    if req_dict.get("currentRole"):
        messages.pop(0)  # Remove the first element
    chat_history.content = json.dumps(messages, ensure_ascii=False)

    # 保存到数据库
    new_id = we_library.add_or_update(chat_history, "chat_history")
    return {
        "resp": resp,
        "id": new_id
    }


@router.post("/chat_role")
async def chat_role():
    # 获取角色列表
    return we_library.fetch_all("SELECT id,role_name,role_setting FROM chat_role", tuple([]))


@router.post("/chat_role_save")
async def chat_role_save(do: ChatRole):
    # 保存修改角色
    return we_library.add_or_update(do, do.table_name)


@router.get("/chat_role_info")
def chat_role_info(id: int):
    # 根据id查询角色
    return we_library.fetch_one(f"SELECT id,role_name,role_setting FROM chat_role WHERE id=?;", (id,))


@router.get("/chat_role_del")
async def chat_role_del(id: int):
    # 删除角色
    we_library.execute_query("DELETE FROM chat_role WHERE id=?;", (id,))
    return True

#
# @router.post("/record")
# async def record(req: BaseReq):
#     # 录制控制
#     return None
#
#
# @router.post("/human")
# async def human(req: BaseReq):
#     # 向数字人发送聊天内容
#     return None
