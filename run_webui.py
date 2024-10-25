import gradio as gr
from gr_module.subtitle_translation import subtitle_translation
from gr_module.video_processing import video_processing
from gr_module.setting import setting
from util import file_util
import os

# 此代理不起作用
# os.environ['HF_ENDPOINT'] = "https://hf-mirror.com/"

# 设置代理

# 临时设置
# 在terminal窗口中运行：$env:HF_ENDPOINT = "https://hf-mirror.com/"
# 然后在窗口中运行程序即可设置临时代理成功

# 永久设置：
# 打开“控制面板”。
# 选择“系统和安全” > “系统” > “高级系统设置”。
# 在“系统属性”窗口中，点击“环境变量”按钮。
# 在“环境变量”窗口中，找到“用户变量”或“系统变量”部分，然后点击“新建”来创建一个新的环境变量。
# 输入变量名 HF_ENDPOINT 和变量值 https://hf-mirror.com/。
# 点击“确定”保存设置。
# 创建gradio页面
with gr.Blocks() as open_webui:
    with gr.Tab("视频处理"):
        video_processing()
    with gr.Tab("字幕翻译"):
        subtitle_translation()
    with gr.Tab("设置"):
        setting()

if __name__ == '__main__':
    open_webui.launch(share=False,
                      server_port=9528,
                      inbrowser=True,
                      favicon_path="./static/icon.ico",
                      allowed_paths=[file_util.get_download_folder()])
