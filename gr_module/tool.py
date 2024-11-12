import gradio as gr
from data import find_duplicates


def tool():
    with gr.Row():
        output = gr.Textbox(lines=1, placeholder="", label="状态")
        with gr.Row():
            with gr.Column(scale=1):
                folder_url = gr.Textbox(lines=1, placeholder="请输入文件夹URL",
                                        label="文件夹URL")
            with gr.Column(scale=2):
                video_run = gr.Button(value="查找重复文件", variant="primary")
            # 查找重复文件
            video_run.click(find_duplicates.run_duplicates, inputs=[folder_url],
                            outputs=[output])
