from faster_whisper import WhisperModel


def transcribe(audio_path, device_type, model_type, task_type, language_type, output_format_type):
    if language_type == "auto":
        language_type = None
    # 指定模型文件的路径
    model_path = "D:\\opt\\faster-whisper\\" + model_type
    # model_path = "base"
    # 加载模型
    model = WhisperModel(model_path, device=device_type, compute_type="int8")

    segments, info = model.transcribe(audio_path, beam_size=5, task=task_type, language=language_type)

    # 输出检测到的语言和概率
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    return f"执行成功\n"
    # 打印每个片段的信息
    # for segment in segments:
    #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
