import gradio as gr
from data import use_fast_whisper, use_whisper, recording
from util import util, json_read


def set_function(selected_type, file_input, device, model, task, language, output_format):
    try:
        if selected_type == "faster_whisper":
            return use_fast_whisper.transcribe(file_input, device, model, task, language, output_format)
        else:
            return use_whisper.transcribe(file_input, device, model, task, language, output_format)
    except Exception as e:
        return "报错：" + str(e)


# 创建gradio页面
with gr.Blocks() as whisper_open_webui:
    with gr.Tab("音视频转录"):
        with gr.Row():
            # 文件上传组件
            file_input = gr.File(label="选择音视频文件")
        with gr.Row():
            run_type = gr.Dropdown(json_read.read_config("type"), value="whisper",
                                   label="类型")
            model = gr.Dropdown(json_read.read_config("model"), value="small",
                                label="模型(转录效果依次增加，但相应花费的时间也会增加)")
        # 使用 gr.Accordion 将 task 和 language 折叠起来
        with gr.Accordion("高级设置", open=False):
            with gr.Row():
                device = gr.Dropdown(json_read.read_config("device"), value="cpu",
                                     label="硬件加速(cuda：显卡，cpu：CPU)")
                task = gr.Dropdown(json_read.read_config("task"), value="transcribe",
                                   label="转录方式(transcribe 转录模式，translate 翻译模式，目前只支持英文)")
            with gr.Row():
                language = gr.Dropdown(
                    json_read.read_config("language"),
                    value="auto", label="指定语言（若不指定默认会截取 30 秒来判断语种）")
        with gr.Row():
            output_format = gr.Dropdown(["srt", "txt"], value="srt", label="输出文件的格式")
        with gr.Row():
            excel_button = gr.Button(value="运行（第一次会下载运行的模型）", variant="primary")
            reset_button = gr.Button(value="打开下载文件夹", variant="primary")
        with gr.Row():
            output = gr.Textbox(lines=3, placeholder="", label="运行状态")
            excel_button.click(set_function, inputs=[run_type, file_input, device, model, task, language,
                                                     output_format], outputs=output)
        reset_button.click(util.open_folder, inputs=[], outputs=[])
    with gr.Tab("实时转录"):
        with gr.Row():
            # outputTab = gr.Textbox(lines=3, placeholder="待开发", label="待开发")
            recording_button = gr.Button("开始/停止录音", variant="primary")
            state_label = gr.Label("等待开始...")

            recording_button.click(
                recording.listen_for_audio,
                inputs=[recording_button],
                outputs=[state_label]
            )

if __name__ == '__main__':
    whisper_open_webui.launch(share=False, server_port=9528, inbrowser=True)