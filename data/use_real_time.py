import sounddevice as sd
import numpy as np
import threading
import time
from faster_whisper import WhisperModel
import requests
import os
import pyttsX

# API URL
API_URL = "http://your-api-url.com/api"

# 麦克风录音参数
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 1  # 持续时间
model_path = "C:\\Users\\1\\.cache\\modelscope\\hub\\pengzhendong\\faster-whisper" + "-medium"

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Faster Whisper 模型初始化
model = WhisperModel(model_path, device="cpu", compute_type="int8")


def recording_transcription(duration, language_type):
    # 识别结果
    recognized_text = ""
    # 录音
    recording = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
    sd.wait()  # 等待录音完成

    # 转换为numpy数组
    audio_data = np.frombuffer(recording, dtype=np.float32).flatten()

    # 语音识别
    segments, info = model.transcribe(audio_data, beam_size=5, language=language_type)
    for segment in segments:
        recognized_text += segment.text + " "
    return recognized_text


def listen_for_audio():
    while True:
        # 录音1秒
        recognized_text = recording_transcription(2, "zh")
        print(recognized_text)
        # 检查是否识别到了关键词
        if "小C" in recognized_text:
            # 生成音频并播放
            pyttsX.speak("我在,你说")
            print("我在")
            # 开始监听5秒 获得语音转录文字
            recognized_text = recording_transcription(5, None)
            print(recognized_text)
            # 调用API
            call_api(recognized_text)


def call_api(recognized_text):
    # 发送POST请求
    response = requests.post(API_URL, data={"text": recognized_text})
    if response.status_code == 200:
        print("API call successful.")
    else:
        print(f"API call failed with status code {response.status_code}.")


def main():
    # 启动监听线程
    thread = threading.Thread(target=listen_for_audio)
    thread.start()

    try:
        while True:
            time.sleep(0.1)  # 减少CPU占用
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
