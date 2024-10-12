import gradio as gr
from data import use_fast_whisper, video_downloader, use_ffmpeg
from util import file_util, json_read

# def set_function(selected_type,file_input, device, model, task, language, output_format):
#     try:
#         if selected_type == "faster_whisper":
#             return use_fast_whisper.transcribe(file_input, device, model, task, language, output_format)
#         else:
#             return use_whisper.transcribe(file_input, device, model, task, language, output_format)
#     except Exception as e:
#         return "报错：" + str(e)


# 创建gradio页面
with gr.Blocks() as open_webui:
    with gr.Tab("视频下载"):
        with gr.Row():
            video_url = gr.Textbox(lines=3, placeholder="请输入Youtube或Bilibili的视频、播放列表或频道的URL",
                                   label="视频URL")
            resolution = gr.Dropdown(json_read.read_config("resolution"), value="1080p", label="分辨率")
            folder_path = gr.Textbox(lines=3, placeholder="默认下载文件夹",
                                     label="输出文件夹")
        with gr.Row():
            video_run = gr.Button(value="运行", variant="primary")
            reset_button = gr.Button(value="打开下载文件夹", variant="primary")
        with gr.Row():
            video_output = gr.Textbox(lines=3, placeholder="", label="运行状态")
            video_run.click(video_downloader.download_from_url, inputs=[video_url, folder_path, resolution],
                            outputs=video_output)

    with gr.Tab("字幕翻译"):
        with gr.Row():
            # 文件上传组件
            file_input = gr.File(label="选择音视频文件")
        with gr.Row():
            # run_type = gr.Dropdown(json_read.read_config("type"), value="whisper",
            #                        label="类型")
            model = gr.Dropdown(json_read.read_config("model"), value="small",
                                label="模型(转录效果依次增加，但相应花费的时间也会增加)")
            output_format = gr.Dropdown(["srt", "txt"], value="srt", label="输出文件的格式")
        # 使用 gr.Accordion 将 task 和 language 折叠起来
        with gr.Accordion("高级设置", open=False):
            with gr.Row():
                device = gr.Dropdown(json_read.read_config("device"), value="cpu",
                                     label="硬件加速(cuda：显卡，cpu：CPU)")
                task = gr.Dropdown(json_read.read_config("task"), value="transcribe",
                                   label="转录方式(transcribe 转录模式，translate 翻译模式，目前只支持英文)")
                language = gr.Dropdown(
                    json_read.read_config("language"),
                    value="auto", label="指定语言（若不指定默认会截取 30 秒来判断语种）")
        with gr.Row():
            excel_button = gr.Button(value="运行（第一次会下载运行的模型）", variant="primary")

        with gr.Row():
            output = gr.Textbox(lines=3, placeholder="", label="运行状态")
        with gr.Row():
            subtitle_input = gr.File(label="选择字幕文件")
            subtitle_button = gr.Button(value="合成字幕", variant="primary")

        subtitle_button.click(use_ffmpeg.add_subtitle, inputs=[file_input,subtitle_input], outputs=output)
        excel_button.click(use_fast_whisper.transcribe, inputs=[file_input, device, model, task, language,
                                                                output_format], outputs=output)
        reset_button.click(file_util.open_folder, inputs=[], outputs=[])

    with gr.Tab("视频处理"):
        with gr.Row():
            # 文件上传组件
            file_input = gr.File(label="选择音视频文件")
            out_folder_path = gr.Textbox(lines=3, placeholder="不填默认下载文件夹",
                                         label="输出文件夹")
        with gr.Row():
            output = gr.Textbox(lines=3, placeholder="", label="状态")
        with gr.Accordion("提取音频", open=False):
            with gr.Row():
                audio_type = gr.Dropdown(json_read.read_config("audio_type"), value="mp3",
                                         label="音频格式")
            with gr.Row():
                excel_button = gr.Button(value="运行", variant="primary")
                excel_button.click(use_ffmpeg.get_audio, inputs=[file_input, audio_type], outputs=output)

        # with gr.Accordion("视频剪辑", open=False):
        #     with gr.Row():
        #         start_time = '00:00:30'
        #         duration = '00:01:00'
        #     with gr.Row():
        #         excel_button = gr.Button(value="运行", variant="primary")
        #         excel_button.click(use_ffmpeg.clip_video, inputs=[file_input, start_time, duration], outputs=output)

        with gr.Accordion("添加音频", open=False):
            with gr.Row():
                input_audio_path = gr.Audio(label="选择音频文件")
            with gr.Row():
                excel_button = gr.Button(value="运行", variant="primary")
                excel_button.click(use_ffmpeg.add_audio, inputs=[file_input, input_audio_path, audio_type],
                                   outputs=output)

        with gr.Accordion("提取视频", open=False):
            with gr.Row():
                video_type = gr.Dropdown(json_read.read_config("video_type"), value="mp4",
                                         label="视频格式")
            with gr.Row():
                excel_button = gr.Button(value="运行", variant="primary")
                excel_button.click(use_ffmpeg.get_video, inputs=[file_input, video_type], outputs=output)


if __name__ == '__main__':
    open_webui.launch(share=False,
                      server_port=9528,
                      inbrowser=True,
                      favicon_path="./static/icon.ico")
