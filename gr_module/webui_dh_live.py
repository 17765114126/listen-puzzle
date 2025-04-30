import gradio as gr

from data import dh_live

initial_md = """

分离音声

"""


def webui_dh_live():
    with gr.Row():
        gr.Markdown(initial_md)

    with gr.Accordion("素材处理"):
        with gr.Row():
            uploaded_audio = gr.Audio(type="filepath", label="待处理音频")
            make_button = gr.Button("分离音频和伴奏")

    with gr.Accordion("人声和伴奏"):
        with gr.Row():
            front_audio = gr.Audio(type="filepath", label="人声歌声")
            back_audio = gr.Audio(type="filepath", label="伴奏")

    with gr.Accordion("合并音频"):
        with gr.Row():
            front1_audio = gr.Audio(type="filepath", label="上传变声")
            merge_button = gr.Button("合并伴奏")
            merge_audio = gr.Audio(type="filepath", label="合并歌曲")

    # 分离音频和伴奏
    make_button.click(dh_live.do_s, inputs=[uploaded_audio], outputs=[front_audio, back_audio])
    # 合并伴奏
    merge_button.click(dh_live.do_m, inputs=[front1_audio, back_audio], outputs=[merge_audio])

# if __name__ == '__main__':
#     app.queue()
#     app.launch(inbrowser=True)
