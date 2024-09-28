import gradio as gr
import os
import json
from data import ollama_api
from util import file_util


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
            filename = f"{first_message[:10]}"
    if filename:
        save_chat(history, filename)
    # 返回更新后的历史记录、多模态文本框和文件名
    return history, gr.MultimodalTextbox(value=None, interactive=False), filename


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
    # selected_row = dataFrame[evt_index]
    selected_row = file_util.get_chats()[evt_index]
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


def del_x(row_index):
    # 在这里实现删除逻辑
    print(f"Deleting row {row_index}")
    return "Row deleted"


# 生成HTML表格的函数
def generate_html_table(data, headers):
    html = '<table>'
    html += '<tr>{}</tr>'.format(''.join(f'<th>{header}</th>' for header in headers))
    for i, row in enumerate(data):
        action1 = f"on_row_click({i})"
        action2 = f"del_x({i})"
        html += f'<tr><td onclick="{action1}">{row[0]}</td><td onclick="{action2}">{row[1]}</td></tr>'
    html += '</table>'
    return html


with gr.Blocks(title="listen-puzzle",theme=gr.themes.Default(primary_hue="gray", secondary_hue="neutral"), css="""
    .wide-first-column td:nth-child(1) {
        width: 95%;
    }
    .wide-first-column td:nth-child(2) {
        width: 5%;
    }
""") as bot_webui:
    gr.Image("E:/img/323578.jpg", height=90, scale=1, label="图片")
    with gr.Tab("对话"):
        with gr.Row():
            with gr.Column(scale=1):
                new_conversation_button = gr.Button(value="新建", variant="primary")
                ollama_model = gr.Dropdown(ollama_api.ollama_list(), value=ollama_api.ollama_list()[0], label="模型")
                refresh_button = gr.Button(value="刷新", variant="primary")
                dataframe_component = gr.DataFrame(
                    value=file_util.get_chats(),
                    headers=["历史记录", "删除"],
                    datatype=["str", "str"],
                    # row_count=2,
                    col_count=(2, "fixed"),
                    label='列表',
                    elem_classes=['wide-first-column']
                )
                # 生成HTML表格
                # html_table = generate_html_table(file_util.get_chats(), ["历史记录", "删除"])
                # gr.HTML(html_table)
            with gr.Column(scale=9):
                chatbot = gr.Chatbot([], elem_id="chatbot", bubble_full_width=True, show_copy_button=True)
                chat_input = gr.MultimodalTextbox(interactive=True, file_types=["image"],
                                                  placeholder="输入消息或上传文件",
                                                  show_label=False)

        # 用于存储当前聊天记录的文件名
        filename_state = gr.State(None)
        # 发送信息记录保存
        chat_msg = chat_input.submit(add_message, [chatbot, chat_input, filename_state],
                                     [chatbot, chat_input, filename_state])
        # 交互大模型
        bot_msg = chat_msg.then(bot, [chatbot, filename_state, ollama_model], chatbot, api_name="bot_response")
        bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])
        # 点赞
        chatbot.like(print_like_dislike, None, None)
        # 刷新按钮点击事件
        refresh_button.click(
            fn=file_util.get_chats,  # 点击按钮时调用的函数
            outputs=[dataframe_component]  # 函数的结果输出到哪个组件
        )
        # 选择聊天记录
        dataframe_component.select(on_row_click, None, [chatbot, filename_state])
        # 绑定新建对话按钮
        new_conversation_button.click(on_new_conversation, [chatbot, chat_input, filename_state],
                                      [chatbot, chat_input, filename_state])

    with gr.Tab("设置"):
        # with gr.Accordion("高级设置", open=False):
        gr.Text(label="token")
if __name__ == '__main__':
    # 启用队列功能
    bot_webui.queue()
    bot_webui.launch(
        share=False,
        server_port=9530,
        inbrowser=True,
        favicon_path="./static/icon.ico"
    )
