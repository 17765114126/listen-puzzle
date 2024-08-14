from faster_whisper import WhisperModel
import os
from util import util


def transcription(audio_data, language_type):
    recognized_text = ""
    # 模型路径 在windows下的缓存路径内
    model_path = "C:/Users/" + os.getlogin() + "/.cache/modelscope/hub/pengzhendong/faster-whisper" + "-" + "base"
    # 加载模型
    model = WhisperModel(model_path, compute_type="int8")
    # 语音识别
    segments, info = model.transcribe(audio_data, beam_size=5, language=language_type)
    # 识别结果
    for segment in segments:
        recognized_text += segment.text + " "
    return recognized_text


def transcribe(audio_path, device_type, model_type, task_type, language_type, output_format_type):
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    if language_type == "auto":
        language_type = None
    # 指定模型文件的路径
    model_path = "D:\\opt\\faster-whisper\\" + model_type
    print(model_path)
    # model_path = "base"
    # 加载模型
    model = WhisperModel(model_path, device=device_type, compute_type="int8")

    segments, info = model.transcribe(audio_path, beam_size=5, task=task_type, language=language_type)

    # 输出检测到的语言和概率
    # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    # 打印每个片段的信息
    # for segment in segments:
    #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

    # 去掉文件名中的后缀
    del_suffix = os.path.splitext(os.path.basename(audio_path))[0]
    # 添加自定义后缀
    add_suffix = "." + output_format_type
    # Windows系统中"C盘/下载"文件夹的通用路径
    download_path = os.path.join('C:\\Users', os.getlogin(), 'Downloads')
    # 指定保存的Excel文件路径
    new_audio_path = os.path.join(download_path, del_suffix + add_suffix)

    # 保存转录结果为txt文件
    if output_format_type == "txt":
        segments_txt = ""
        for segment in segments:
            segments_txt += segment.text + "\n"
        with open(new_audio_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(segments_txt)
    # 保存转录结果为SRT文件
    if output_format_type == "srt":
        util.segments_to_srt(segments, new_audio_path)
    return f"执行成功\n"


def speak(audio_data):
    # 判断录音中是否有人说话

    # 计算音频信号的绝对值
    abs_audio_data = np.abs(audio_data)

    # 计算平均振幅
    average_amplitude = np.mean(abs_audio_data)

    # 设定阈值
    threshold = 0.05  # 需要根据实际情况调整

    # 判断是否有人说话
    if average_amplitude > threshold:
        print("录音中有说话的声音")
        return True
    else:
        print("录音中没有人说话")
        return False
