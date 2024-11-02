import gradio as gr

from audio_separator.separator import Separator

from pydub import AudioSegment


def do_s(audio):
    output = "separated_audio"
    separator = Separator(model_file_dir="D:/hf-model/separated_model/", output_dir=output)

    separator.load_model()

    outfiles = separator.separate(audio)

    print(outfiles)
    return f"separated_audio/{outfiles[1]}", f"separated_audio/{outfiles[0]}"


def do_m(audio, back):
    # 加载背景音乐和人声文件
    background_music = AudioSegment.from_file(back)
    vocal = AudioSegment.from_file(audio)

    # 合并音频文件
    combined_audio = background_music.overlay(vocal)

    # 导出合并后的音频文件
    combined_audio.export("combined_audio.wav", format="wav")

    return "combined_audio.wav"


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

    make_button.click(do_s, inputs=[uploaded_audio], outputs=[front_audio, back_audio])
    merge_button.click(do_m, inputs=[front1_audio, back_audio], outputs=[merge_audio])

# if __name__ == '__main__':
#     app.queue()
#     app.launch(inbrowser=True)
