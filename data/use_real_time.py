import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import os

# 麦克风录音参数
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 1  # 持续时间
# 模型路径 在windows下的缓存路径内
model_path = os.environ['LOCALAPPDATA'] + ".cache\\modelscope\\hub\\pengzhendong\\faster-whisper" + "-" + "medium"

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Faster Whisper 模型初始化
model = WhisperModel(model_path, device="cpu", compute_type="int8")


def recording(duration):
    # 录音
    record = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
    sd.wait()  # 等待录音完成

    # 转换为numpy数组
    audio_data = np.frombuffer(record, dtype=np.float32).flatten()
    return audio_data


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


def transcription(audio_data, language_type):
    recognized_text = ""
    # 语音识别
    segments, info = model.transcribe(audio_data, beam_size=5, language=language_type)
    # 识别结果
    for segment in segments:
        recognized_text += segment.text + " "
    return recognized_text


def listen_for_audio(bool):
    while True:
        # 录音1秒
        audio_data = recording(1)
        # 判断是否有人声
        if (speak(audio_data)):
            # 识别
            recognized_text = transcription(audio_data, "zh")
            print(recognized_text)
