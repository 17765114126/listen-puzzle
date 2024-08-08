import gradio as gr
from data import use_fast_whisper, use_whisper
from util import util, json_read

# 创建gradio页面
with gr.Blocks() as whisper_open_webui:
    with gr.Row():
        # 创建文件上传组件
        file_input = gr.File(label="选择文件")
        # cookie = gr.Textbox(lines=2, placeholder="", label="cookie")
        device_type = gr.Dropdown(json_read.read_config("type"), value="whisper",
                                  label="类型")
    with gr.Row():
        device = gr.Dropdown(json_read.read_config("device"), value="cpu",
                             label="硬件加速(cuda：显卡，cpu：CPU)")

        model = gr.Dropdown(json_read.read_config("model"), value="small",
                            label="模型(转录效果依次增加，但相应花费的时间也会增加)")
    with gr.Row():
        task = gr.Dropdown(json_read.read_config("task"), value="transcribe",
                           label="转录方式(transcribe 转录模式，translate 则为翻译模式，目前只支持英文。)")
        language = gr.Dropdown(
            json_read.read_config("language"),
            value="auto", label="指定语言（若不指定默认会截取 30 秒来判断语种）")
    with gr.Row():
        output_format = gr.Dropdown(["srt", "txt"], value="srt", label="输出文件的格式")

    with gr.Row():
        excel_button = gr.Button(value="运行（第一次运行会下载模型）", variant="primary")
        reset_button = gr.Button(value="打开下载文件夹", variant="primary")
    with gr.Row():
        output = gr.Textbox(label="运行状态")
    if device_type == "whisper":
        excel_button.click(use_whisper.transcribe, inputs=[file_input, device, model, task, language, output_format],
                           outputs=output)
    else:
        excel_button.click(use_fast_whisper.transcribe, inputs=[file_input, device, model, task, language,
                                                                output_format], outputs=output)
    reset_button.click(util.open_folder, inputs=[], outputs=[])

if __name__ == '__main__':
    whisper_open_webui.launch(share=False, server_port=9528)
