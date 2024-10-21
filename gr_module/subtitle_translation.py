import gradio as gr
from data import use_fast_whisper, use_ffmpeg
from util import file_util
import config


# def set_function(selected_type,file_input, device, model, task, language, output_format):
#     try:
#         if selected_type == "faster_whisper":
#             return use_fast_whisper.transcribe(file_input, device, model, task, language, output_format)
#         else:
#             return use_whisper.transcribe(file_input, device, model, task, language, output_format)
#     except Exception as e:
#         return "报错：" + str(e)

def subtitle_translation():
    with gr.Row():
        with gr.Column():
            with gr.Row():
                file_input = gr.File(label="选择音视频文件")
                subtitle_input = gr.File(label="选择字幕文件")
            gr.Markdown(value="字幕文件")
            with gr.Row():
                # run_type = gr.Dropdown(json_read.read_config("type"), value="whisper", label="类型")
                with gr.Column(scale=1):
                    model = gr.Dropdown(config.whisper_model, value="small",
                                        label="模型(转录效果依次增加，但相应花费的时间也会增加)")
                    output_format = gr.Dropdown(["srt", "txt"], value="srt", label="输出文件的格式")
                # 使用 gr.Accordion 将 task 和 language 折叠起来
                with gr.Column(scale=2):
                    with gr.Accordion("高级设置", open=True):
                        device = gr.Dropdown(config.whisper_device, value="cpu",
                                             label="硬件加速(cuda：显卡，cpu：CPU)")
                        language = gr.Dropdown(
                            config.whisper_language,
                            value="auto", label="指定语言（若不指定默认会截取 30 秒来判断语种）")
                    # excel_button = gr.Button(value="运行（第一次会下载运行的模型）", variant="primary")
            is_translate = gr.Checkbox(label="是否翻译", value=False)
            with gr.Accordion("翻译设置", open=False):
                with gr.Row():
                    with gr.Column(scale=1):
                        translator_engine = gr.Dropdown(
                            config.translator_engine,
                            value="bing", label="翻译引擎")
                    with gr.Column(scale=2):
                        subtitle_language = gr.Dropdown(
                            config.translator_language,
                            value="zh", label="目标语言")
                    with gr.Column(scale=3):
                        subtitle_double = gr.Checkbox(label="双语对照", value=False)
            excel_button = gr.Button(value="生成字幕文件（第一次会下载模型）", variant="primary")
            with gr.Row():
                with gr.Accordion("字幕设置", open=False):
                    is_soft = gr.Checkbox(label="软字幕", value=False)
                    font_size = gr.Number(label="字幕大小", value=16)
                subtitle_button = gr.Button(value="合成字幕", variant="primary")

        with gr.Column(variant="panel", elem_classes="right-column"):
            output = gr.Textbox(lines=3, placeholder="", label="运行状态")
            # reset_button = gr.Button(value="打开下载文件夹", variant="primary")
            # # 打开下载文件夹
            # reset_button.click(file_util.open_folder, inputs=[], outputs=[])
            gr.Markdown(value="字幕文件预览")
            subtitle_content = gr.Textbox(label="字幕内容", lines=30, interactive=True)
            save_button = gr.Button(value="保存文件", variant="primary")
    # 保存文件
    save_button.click(fn=file_util.save_text_file, inputs=[subtitle_content], outputs=output)
    # 选中字幕文件 将内容添加到预览
    subtitle_input.change(fn=file_util.read_text_file, inputs=[subtitle_input], outputs=[subtitle_content])
    # 视频合成字幕
    subtitle_button.click(use_ffmpeg.add_subtitle, inputs=[file_input, subtitle_content, is_soft, font_size],
                          outputs=output)
    # 音视频转录文字
    excel_button.click(use_fast_whisper.transcribe, inputs=[file_input, device, model, language,
                                                            output_format, is_translate, subtitle_double,
                                                            translator_engine,
                                                            subtitle_language], outputs=[output, subtitle_content])
