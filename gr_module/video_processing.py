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
            video_input = gr.Video(label="视频预览", interactive=True)
    with gr.Row():
        with gr.Accordion("常用", open=True):
            with gr.Row():
                with gr.Column(scale=1):
                    input_audio = gr.Audio(label="选择音频文件")
                    add_audio_to_video_button = gr.Button(value="添加音频", variant="primary")
                with gr.Column(scale=1):
                    start_time = gr.Textbox(label="开始时间 (格式: HH:MM:SS)", placeholder="00:00:10", value="00:00:10")
                    end_time = gr.Textbox(label="结束时间 (格式: HH:MM:SS)", placeholder="00:00:30", value="00:00:30")
                    cut_button = gr.Button("剪切视频")
                with gr.Column(scale=1):
                    video_type = gr.Dropdown(
                        config.video_type,
                        value="mp4", label="视频格式")
                    video_format_button = gr.Button(value="视频格式转化", variant="primary")
    with gr.Accordion("其他", open=False):
        with gr.Row():
            with gr.Column(scale=1):
                video_info_button = gr.Button(value="视频信息", variant="primary")
                get_audio_button = gr.Button(value="提取音频", variant="primary")
                get_video_button = gr.Button(value="提取视频", variant="primary")
                time_ss = gr.Textbox(label="秒数 (格式: HH:MM:SS)", placeholder="00:00:10", value="00:00:10")
                extract_frame_button = gr.Button(value="提取图片", variant="primary")
            with gr.Column(scale=1):
                cover_image = gr.File(label="选择封面图")
                video_cover_button = gr.Button(value="设置封面图", variant="primary")
            with gr.Column(scale=1):
                audio_volume = gr.Number(label="音量", minimum=1, maximum=5, step=0.1, value=1)
                audio_volume_button = gr.Button(value="音量调整", variant="primary")
                speed_video = gr.Number(label="速度", minimum=0.5, maximum=2.0, step=0.1, value=1)
                speed_video_button = gr.Button(value="速度调整", variant="primary")
    # 速度调整
    speed_video_button.click(use_ffmpeg.speed_video, inputs=[video_input, speed_video],
                             outputs=output)
    # 音量调整
    audio_volume_button.click(use_ffmpeg.adjust_audio_volume, inputs=[video_input, audio_volume],
                              outputs=output)
    # 提取图片
    extract_frame_button.click(use_ffmpeg.extract_frame, inputs=[video_input, time_ss],
                               outputs=output)
    # 设置封面图
    video_cover_button.click(use_ffmpeg.set_video_cover, inputs=[video_input, cover_image],
                             outputs=output)
    # 提取视频
    get_video_button.click(use_ffmpeg.get_video, inputs=[video_input], outputs=output)
    # 提取音频
    get_audio_button.click(use_ffmpeg.get_audio, inputs=[video_input], outputs=output)
    # 视频格式转化
    video_format_button.click(use_ffmpeg.convert_video_format, inputs=[video_input, video_type],
                              outputs=output)
    # 剪切视频
    cut_button.click(use_ffmpeg.cut_video, inputs=[video_input, start_time, end_time],
                     outputs=output)
    # 添加音频
    add_audio_to_video_button.click(use_ffmpeg.add_audio_to_video, inputs=[video_input, input_audio],
                                    outputs=output)
    # 视频信息
    video_info_button.click(use_ffmpeg.get_info, inputs=[video_input], outputs=output)
    # 下载视频
    video_run.click(video_downloader.download_videos_from_urls, inputs=[video_url, resolution],
                    outputs=[output, video_input])
