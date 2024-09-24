import gradio as gr
import os
import json
import time
from data import ollama_api
from util import file_util

dataFrame = file_util.get_chats()


def print_like_dislike(x: gr.LikeData):
    # 定义一个函数，打印用户对聊天机器人回复的点赞或点踩的数据
    print(x.index, x.value, x.liked)


def add_message(history, message, filename=None):
    # 遍历消息中的文件
    for x in message["files"]:
        # 将文件添加到历史记录中
        history.append(((x,), None))
        # 如果消息中包含文本
    if message["text"] is not None:
        # 将文本消息添加到历史记录中
        history.append((message["text"], None))
        # 如果是第一条消息，创建新文件名
    if filename is None and len(history) == 1:
        first_message = history[0][0]
        if isinstance(first_message, str):
            filename = f"{first_message[:5]}"
    if filename:
        save_chat(history, filename)
    # 返回更新后的历史记录、多模态文本框和文件名
    return history, gr.MultimodalTextbox(value=None, interactive=False), filename


def save_chat(chat, filename):
    with open("chats/" + filename, "w", encoding="utf-8") as f:
        json.dump(chat, f, ensure_ascii=False, indent=4)


def bot(history, filename, ollama_model):
    print("模型：" + ollama_model)
    # 机器人的响应文本
    response = "**That's cooldfb开始不断步!**"
    # 将用户的最后一条消息和机器人的回复作为一对添加到 history 中
    if history and isinstance(history[-1], list) and len(history[-1]) == 2:
        history[-1][1] = response

    # time.sleep(0.05)  # 每添加一个字符后暂停0.05秒
    # 生成更新后的历史记录
    yield history
    if filename:
        save_chat(history, filename)


def on_new_conversation(chatbot, chat_input, filename_state):
    # 清空聊天记录
    chatbot = []
    # 重置输入框
    chat_input = {"text": "", "files": []}
    # 聊天记录名称重置
    filename_state = None
    return chatbot, chat_input, filename_state


def on_row_click(evt: gr.SelectData):
    evt_index = evt.index[0]
    # 获取被点击行的数据
    selected_row = dataFrame[evt_index]
    # 获取文件名
    filename = selected_row[0]
    # 加载聊天记录
    chat_history = load_chat(f"chats/{filename}")
    # 返回选中的文件名
    return chat_history, filename


def load_chat(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


with gr.Blocks() as bot_webui:
    gr.Image("D:/opt/3.jpg", height=90, scale=1, label="图片")
    with gr.Row():
        with gr.Column(scale=1):
            new_conversation_button = gr.Button(value="新建对话", variant="primary")
            ollama_model = gr.Dropdown(ollama_api.ollama_list(), value="Llama 3.1", label="模型")

            dataframe_component = gr.DataFrame(
                value=dataFrame,
                headers=["历史记录"],
                datatype=["str"],
                # row_count=2,
                col_count=(1, "fixed"),
                label='列表'
            )

            # output_text = gr.Textbox(label="Selected Name")
            with gr.Accordion("高级设置", open=False):
                gr.Text(label="token")

        with gr.Column(scale=2):
            chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=True)
            chat_input = gr.MultimodalTextbox(interactive=True, file_types=["image"],
                                              placeholder="输入消息或上传文件",
                                              show_label=False)

    # 用于存储当前聊天记录的文件名
    filename_state = gr.State(None)
    chat_msg = chat_input.submit(add_message, [chatbot, chat_input, filename_state],
                                 [chatbot, chat_input, filename_state])
    bot_msg = chat_msg.then(bot, [chatbot, filename_state, ollama_model], chatbot, api_name="bot_response")
    bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])
    # 点赞
    chatbot.like(print_like_dislike, None, None)
    # 选择聊天记录
    dataframe_component.select(on_row_click, None, [chatbot, filename_state])
    # 绑定新建对话按钮
    new_conversation_button.click(on_new_conversation, [chatbot, chat_input, filename_state],
                                  [chatbot, chat_input, filename_state])
if __name__ == '__main__':
    bot_webui.queue()  # 启用队列功能
    bot_webui.launch(
        share=False,
        server_port=9530,
        inbrowser=True,
        favicon_path="./static/icon.ico"
    )
