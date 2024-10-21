import gradio as gr
import config


def setting():
    with gr.Row():
        device1 = gr.Dropdown(config.whisper_device, value="qwen",
                              label="大模型选择")
