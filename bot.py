import gradio as gr
import os
import json
from data import ollama_api
from util import file_util


# def print_like_dislike(x: gr.LikeData):
#     # 定义一个函数，打印用户对聊天机器人回复的点赞或点踩的数据
#     print(x.index, x.value, x.liked)


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
            filename = f"{first_message[:10]}"
    if filename:
        save_chat(history, filename)
    # 返回更新后的历史记录、多模态文本框和文件名
    return history, gr.MultimodalTextbox(value=None, interactive=False), filename, file_util.get_chats()


def save_chat(chat, filename):
    with open("chats/" + filename, "w", encoding="utf-8") as f:
        json.dump(chat, f, ensure_ascii=False, indent=4)


def bot(history, filename, ollama_model):
    messages = []
    for x in history:
        messages.append({
            'role': 'user',
            'content': x[0]
        })
        if x[1] is not None:
            messages.append({
                'role': 'assistant',
                'content': x[1]
            })


    # 机器人的响应文本
    # response = "**That's cooldfb开始不断步!**"
    response = ollama_api.ollama_chat(ollama_model, messages)
    # 将用户的最后一条消息和机器人的回复作为一对添加到 history 中
    if history and isinstance(history[-1], list) and len(history[-1]) == 2:
        history[-1][1] = response
    # 生成更新后的历史记录
    # import time
    # time.sleep(0.05)  # 每添加一个字符后暂停0.05秒
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
    # 获取被点击行的索引
    evt_index = evt.index[0]
    # 获取被点击列的索引
    col_index = evt.index[1]
    selected_row = file_util.get_chats()[evt_index]
    # 获取文件名
    filename = selected_row[0]
    if col_index == 0:
        # 加载聊天记录
        chat_history = load_chat(f"chats/{filename}")
        # 返回选中的文件名
        return chat_history, filename, file_util.get_chats()
    elif col_index == 1:
        # 用户点击了第二列（删除）
        file_util.del_file(f"chats/{filename}")
        return [], None, file_util.get_chats()  # 清空聊天bot和重置filename_state


def load_chat(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


# orange    green emerald     teal  cyan

dark_theme = gr.themes.Base(
    # primary_hue=gr.themes.colors.orange,
    # secondary_hue=gr.themes.colors.orange,
    neutral_hue=gr.themes.colors.teal,
)
css = """
    .wide-first-column td:nth-child(1) {
        width: 95%;
    }
    .wide-first-column td:nth-child(2) {
        width: 5%;
    }
"""
with gr.Blocks(title="listen-puzzle", theme=dark_theme, css=css) as bot_webui:
    markdown = gr.Markdown(
        """
        # 自定义大模型 WebUI V1.0
        后续将添加功能
        - 流式返回信息
        - 图片发送
        - 图片生成
        - 样式优化
        - 语音对话模式
        - 模型工具调用
        - 创建自定义模型
        """,
        label="自定义大模型webui"
    )
    with gr.Tab("聊天模式"):
        with gr.Row():
            with gr.Column(scale=1):
                new_conversation_button = gr.Button(value="新建对话")
                ollama_model = gr.Dropdown(ollama_api.ollama_list(), value=ollama_api.ollama_list()[0], label="模型")
                dataframe_component = gr.DataFrame(
                    value=file_util.get_chats(),
                    headers=["历史记录", "删除"],
                    datatype=["str", "str"],
                    col_count=(2, "fixed"),
                    label='列表',
                    elem_classes=['wide-first-column']
                )
            with gr.Column(scale=9):
                chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=True, show_copy_button=True)
                chat_input = gr.MultimodalTextbox(interactive=True, file_types=["image"],
                                                  placeholder="输入消息或上传文件",
                                                  show_label=False)

        # 用于存储当前聊天记录的文件名
        filename_state = gr.State(None)
        # 发送信息记录保存
        chat_msg = chat_input.submit(add_message, [chatbot, chat_input, filename_state],
                                     [chatbot, chat_input, filename_state, dataframe_component])
        # 交互大模型
        bot_msg = chat_msg.then(bot, [chatbot, filename_state, ollama_model], chatbot, api_name="bot_response")
        bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])
        # 点赞
        # chatbot.like(print_like_dislike, None, None)
        # 选择聊天记录
        dataframe_component.select(on_row_click, None, [chatbot, filename_state, dataframe_component])
        # 绑定新建对话按钮
        new_conversation_button.click(on_new_conversation, [chatbot, chat_input, filename_state],
                                      [chatbot, chat_input, filename_state])
    with gr.Tab("语音模式"):
        gr.Audio(label="音频文件")
    with gr.Tab("设置"):
        # with gr.Accordion("高级设置", open=False):
        # gr.Text(label="token")
        output_text = gr.Textbox(label="输出信息")
        with gr.Row():
            model_name = gr.Text(label="模型名称")
            pull_button = gr.Button(value="拉取模型")
        with gr.Row():
            del_model = gr.Dropdown(ollama_api.ollama_list(), value=ollama_api.ollama_list()[0], label="删除模型")
            del_button = gr.Button(value="删除模型")
        # 将按钮点击绑定到pull_model函数
        pull_button.click(fn=ollama_api.ollama_pull, inputs=model_name, outputs=output_text)
        # 将按钮点击绑定到del_model函数
        del_button.click(fn=ollama_api.ollama_delete, inputs=del_model, outputs=output_text)
if __name__ == '__main__':
    # 启用队列功能
    bot_webui.queue()
    bot_webui.launch(
        share=False,
        server_port=9530,
        inbrowser=True,
        favicon_path="./static/icon.ico"
    )
