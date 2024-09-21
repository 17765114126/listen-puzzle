import gradio as gr
import random
import time
import numpy as np

'''
Button：创建一个可点击的按钮，用于触发特定的动作或事件。
Radio：供单选按钮，允许用户从多个选项中选择一个。
Checkbox：提供一个复选框，允许用户选择或取消选择一个选项。
CheckboxGroup：复选框组
Dropdown：提供一个下拉菜单，允许用户从预定义的选项中选择一个。
Slider：提供一个滑动条，允许用户通过拖动滑块来选择一个范围内的值。
DateTime：允许用户选择日期和时间。
Number：允许用户输入数字。

Text：允许用户输入单行文本。
Textbox：允许用户输入多行文本。
File：允许用户上传文件。
Video：用于播放视频文件。
Audio：用于播放音频文件。

ClearButton：创建一个清除按钮，用于清除输入框或其他组件的内容。
UploadButton：创建一个上传按钮，允许用户上传文件到服务器。
DuplicateButton：创建一个复制按钮，用于复制选定的内容或元素。
DownloadButton：创建一个下载按钮，用于下载文件或数据。
LoginButton：创建一个登录按钮，用于用户身份验证。
LogoutButton：创建一个登出按钮，用于用户退出登录状态。
Label：展示文本标签，用于说明或标注其他组件。

DataFrame：列表
Timer：显示一个计时器，可以用于计时或倒计时。
Chatbot：实现一个聊天机器人界面，与用户进行对话。
ChatMessage：展示聊天消息，包括发送者、接收者和消息内容。

HTML：允许嵌入HTML代码，用于创建自定义的HTML内容。
JSON：用于展示或输入JSON格式的数据。
AnnotatedImage：展示一张带有标注（如矩形框、多边形等）的图片。
Annotatedimage（可能是AnnotatedImage的重复或变体）：同上，用于展示带标注的图片。
BarPlot：展示条形图，用于比较不同类别的数据。
Plot：展示各种类型的图表，如折线图、柱状图等。
LinePlot：展示折线图，用于可视化数据随时间的变化趋势。
ScatterPlot：展示散点图，用于可视化两个变量之间的关系。


Code：展示代码片段，通常用于编程环境或教程。
Markdown：允许输入和展示Markdown格式的文本。
ColorPicker：允许用户选择颜色，常用于图形设计或配置界面。

Dataset：表示一个数据集，用于存储和操作大量数据。
FileExplorer：展示一个文件浏览器界面，用于浏览和管理文件系统中的文件。

Image：展示一张图片。
ImageEditor：提供一个图像编辑界面，允许用户编辑图片。
Gallery：展示一个图片画廊，允许用户浏览和切换多张图片。
Highlight：对文本进行高亮显示，以突出重要信息。


MessageDict：可能是一个用于存储和展示消息字典的组件。
Model3D：展示三维模型，常用于产品展示或虚拟现实应用。
ParamViewer：可能是一个用于查看和编辑参数的组件。
State：用于保存和恢复组件的状态信息。

MultimodalTextbox：提供一个多模态文本框，可能支持文本、图像等多种输入方式。

'''


def user(user_message, history):
    return "", history + [[user_message, None]]


def bot(history):
    bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
    time.sleep(2)
    history[-1][1] = bot_message
    return history


def html_content():
    return """
    <h1>Hello, Gradio Blocks!</h1>
    <p>This is an example of using the <code>gradio.HTML</code> component in Gradio Blocks.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    """


def line_plot_data():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    return x, y


def chat_message_data():
    return {
        "sender": "User",
        "message": "Hello, Gradio Blocks!"
    }


# 创建gradio页面
with gr.Blocks() as demo_webui:
    with gr.Tab("Demo"):
        with gr.Accordion("折叠组件", open=True):
            with gr.Row():
                gr.Code(label="代码块")
                with gr.Group():
                    gr.Number(label="数字")
                    gr.DateTime(label="日期", include_time=False)
                    gr.DateTime(label="日期和时间")
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("Chatbot")
                gr.Label(value="文本标签")
                gr.Text(label="单行文本框")
                gr.Textbox(label="多行文本框")
                gr.Slider(1, 10, step=2, interactive=True, label="滑块")
                gr.MultimodalTextbox()
            with gr.Column(scale=2):
                gr.Radio(["提取音频", "提取视频"], label="单选框")
                gr.Checkbox(label="复选框：选择或取消选项")
                gr.Checkboxgroup(["提取音频", "提取视频"], label="复选框组")
                gr.Dropdown(["mp3", "wav", "acc"], value="mp3", label="下拉")
                gr.ColorPicker(label="颜色选取器")
        with gr.Row():
            gr.File(label="音视频文件")
            gr.FileExplorer(label="文件")
            gr.Audio(label="音频文件")
            gr.Video(label="视频文件")
            # gr.Markdown(label="Markdown")
        with gr.Row():
            dataFrame = [
                ["Bob", 25, "Male"],
                ["David", 28, "Male"],
            ]
            gr.DataFrame(
                value=dataFrame,
                headers=["name", "age", "gender"],
                datatype=["str", "number", "str"],
                row_count=2,
                col_count=(3, "fixed"),
                label='列表')
            data = [
                {"name": "Alice", "age": 30, "gender": "Female"},
                {"name": "Bob", "age": 25, "gender": "Male"},
            ]
            # gr.Timer() # 定时器
            # 将数据集转换为 gr.Dataset 对象
            # dataset = gr.Dataset(data)
            # 条形图
            # gr.BarPlot()
            # 线图
            # gr.LinePlot(label="Line Plot")
            # 模型3D
            # gradio.Model3D()
            # 绘图
            # gr.Plot()
            # 散点图
            # gr.ScatterPlot()

        with gr.Row():
            # gr.Image("D:/opt/3.jpg", scale=1, label="图片")
            gr.Image(scale=1, label="图片")
            gr.ImageEditor(scale=1, label="图片编辑器")
            gr.Gallery(label="画廊")
        with gr.Row():
            gr.Button(value="运行", variant="primary")
            gr.ClearButton(value="清除")
            gr.DuplicateButton(value="复制")
            gr.UploadButton(label="上传")
            gr.DownloadButton(label="下载")
            # gr.LoginButton(value="登录")
            # gr.LogoutButton(value="登出")
        with gr.Row():
            html_output = gr.HTML(label="HTML Content")
            html_button = gr.Button("Show HTML")
            html_button.click(html_content, outputs=html_output)
    with gr.Tab("机器人"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        clear = gr.Button("清空")

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)
    # with gr.Tab("聊天"):
    #     gr.ChatMessage()

if __name__ == '__main__':
    demo_webui.launch(share=False, server_port=9529, inbrowser=True)
