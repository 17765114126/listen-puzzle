import whisper
import os
# from util import file_util
# import pyaudio
# import wave
# import numpy as np
# import librosa


# 转录语音为文字
def transcribe(audio_path, device_type, model_type, task_type, language_type, output_format_type):
    if language_type == "auto":
        language_type = None

    # 指定模型，硬件加速，模型地址
    model = whisper.load_model(
        name=model_type,
        device=device_type,
        # download_root="C:\\Users\\1\\AppData\\Local\\Buzz\\Buzz\\Cache\\models\\whisper"
    )
    result = model.transcribe(
        audio=audio_path,
        task=task_type,  # transcribe 转录模式，translate 翻译模式，目前只支持英文。
        # fp16=False,  # 是否使用 fp16 模式
        verbose=False,  # 控制台是否打印输出
        language=language_type,  # 指定语言
        # without_timestamps=False,  # 是否去除时间戳
        # max_initial_timestamp=0.0,  # 最大初始时间戳
        # word_timestamps=False,  # 是否输出字幕时间戳
        # temperature=0.0,  # 随机温度
        # best_of=5,  # 输出结果数量
        # beam_size=5,  # 输出结果数量
    )

    # 去掉文件名中的后缀
    del_suffix = os.path.splitext(os.path.basename(audio_path))[0]
    # 添加自定义后缀
    add_suffix = "." + output_format_type
    # new_audio_path = os.path.join(os.path.dirname(audio_path), del_suffix + add_suffix)

    # Windows系统中"C盘/下载"文件夹的通用路径
    download_path = os.path.join('C:\\Users', os.getlogin(), 'Downloads')
    # 指定保存的Excel文件路径
    new_audio_path = os.path.join(download_path, del_suffix + add_suffix)

    # 保存转录结果为txt文件
    if output_format_type == "txt":
        with open(new_audio_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(result["text"])
    # 保存转录结果为SRT文件
    if output_format_type == "srt":
        out_srt_file(result["segments"], new_audio_path)
    return f"执行成功：文本为：\n" + result["text"]


# 保存转录结果为SRT文件
def out_srt_file(segments, output_srt_file):
    with open(output_srt_file, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            start_time = segment['start']
            end_time = segment['end']
            start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
            end_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"
            subtitle_text = segment["text"].strip()
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_str} --> {end_str}\n")
            srt_file.write(f"{subtitle_text}\n\n")
