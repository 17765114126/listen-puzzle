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


def listen_for_audio():
    while True:
        # 录音1秒
        audio_data = recording(1)
        # 判断是否有人声
        if(speak(audio_data)):
            recognized_text = transcription(audio_data, "zh")
            print(recognized_text)
            # 检查是否识别到了关键词
            if "小C" in recognized_text:
                # 生成音频并播放
                pyttsX.speak("我在,你说")
                print("我在")
                # 开始监听5秒 获得语音转录文字

                audio_data = recording(5)
                if (speak(audio_data)):
                    recognized_text = transcription(audio_data, None)
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
