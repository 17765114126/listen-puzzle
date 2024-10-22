import gradio as gr
from data import video_downloader, use_ffmpeg
import config


def video_processing():
    with gr.Row():
        with gr.Column(scale=1):
            video_url = gr.Textbox(lines=1, placeholder="请输入Youtube或Bilibili的视频、播放列表或频道的URL",
                                   label="视频URL")
            resolution = gr.Dropdown(config.resolution, value="1080p", label="分辨率")
            video_run = gr.Button(value="视频下载", variant="primary")
            output = gr.Textbox(lines=1, placeholder="", label="状态")
        with gr.Column(scale=2):
            # 文件上传组件
            # file_input = gr.File(label="选择音视频文件")
            # 视频播放器
            video_input = gr.Video(label="视频预览", interactive=True)

    with gr.Row():
        with gr.Accordion("提取音频", open=False):
            with gr.Row():
                audio_type = gr.Dropdown(config.audio_type, value="mp3",
                                         label="音频格式")
            with gr.Row():
                excel_button = gr.Button(value="运行", variant="primary")
                excel_button.click(use_ffmpeg.get_audio, inputs=[video_input, audio_type], outputs=output)

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
            excel_button.click(use_ffmpeg.add_audio, inputs=[video_input, input_audio_path, audio_type],
                               outputs=output)
    with gr.Accordion("提取视频", open=False):
        with gr.Row():
            video_type = gr.Dropdown(config.video_type, value="mp4",
                                     label="视频格式")
        with gr.Row():
            excel_button = gr.Button(value="运行", variant="primary")
            excel_button.click(use_ffmpeg.get_video, inputs=[video_input, video_type], outputs=output)
    # 下载视频
    video_run.click(video_downloader.download_videos_from_urls, inputs=[video_url, resolution],
                    outputs=[output, video_input])
