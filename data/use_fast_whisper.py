from faster_whisper import WhisperModel
import os
from util import file_util, download_model
from data import use_translation


def transcribe(audio_path, device_type, model_type, language_type, output_format_type, is_translate, subtitle_double,
               translator_engine, subtitle_language):
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    if language_type == "auto":
        language_type = None
    # 指定模型文件的路径
    # model_path = "D:\\opt\\faster-whisper\\" + model_type
    model_path = "C:/Users/" + os.getlogin() + "/.cache/modelscope/hub/pengzhendong/faster-whisper" + "-" + model_type
    if not file_util.check_folder(os.path.join(model_path, "model.bin")):
        download_model.download_model(model_type)
        return f"正在下载模型{model_path}，请下载完毕后重试(可在控制台查看下载进度)"
    # 加载模型
    model = WhisperModel(model_path, device=device_type, compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=5, task="transcribe", language=language_type)

    # txt文件
    segments_txt = ""
    if output_format_type == "txt":
        for segment in segments:
            if is_translate:
                # 翻译
                if subtitle_double:
                    # 双语字幕
                    segments_txt += segment.text + "\n"
                segments_txt += use_translation.translator_response(segment.text, subtitle_language,
                                                                    translator_engine) + "\n"
            else:
                # 原文
                segments_txt += segment.text + "\n"
    # SRT文件
    if output_format_type == "srt":
        for i, segment in enumerate(segments, start=1):
            start_time = segment.start
            end_time = segment.end
            start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
            end_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"
            subtitle_text = segment.text.strip()
            segments_txt += f"{i}\n"
            segments_txt += f"{start_str} --> {end_str}\n"
            if is_translate:
                if subtitle_double:
                    # 双语字幕
                    segments_txt += f"{subtitle_text}\n"
                # 翻译
                segments_txt += use_translation.translator_response(subtitle_text, subtitle_language,
                                                                    translator_engine) + "\n\n"
            else:
                # 原文
                segments_txt += f"{subtitle_text}\n\n"
    return f"执行成功\n", segments_txt
