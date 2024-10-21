import gradio as gr
from gr_module.subtitle_translation import subtitle_translation
from gr_module.video_processing import video_processing
from gr_module.setting import setting

# 创建gradio页面
with gr.Blocks() as open_webui:
    with gr.Tab("字幕翻译"):
        subtitle_translation()
    with gr.Tab("视频处理"):
        video_processing()
    with gr.Tab("设置"):
        setting()


if __name__ == '__main__':
    open_webui.launch(share=False,
                      server_port=9528,
                      inbrowser=True,
                      favicon_path="./static/icon.ico")
