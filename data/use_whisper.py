import whisper
import os
from util import util
import pyaudio
import wave
import numpy as np
import librosa


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
        util.out_srt_file(result["segments"], new_audio_path)
    return f"执行成功：文本为：\n" + result["text"]


# 设置音频参数
FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1  # 单声道
# RATE = 44100 # 采样率，这里是44.1kHz
RATE = 16000
CHUNK = 1024  # 数据块大小
RECORD_SECONDS = 5  # 录制5秒
# 初始化pyaudio
audio = pyaudio.PyAudio()


# 音频转文字
def file_to_text(mp3Url):
    # 加载模型
    model = whisper.load_model("small")
    # result = model.transcribe(mp3Url, language="Chinese")
    result = model.transcribe(mp3Url)
    print(", ".join([i["text"] for i in result["segments"] if i is not None]))


# 音频数据处理
def audio_data_dispose(audio_data):
    # 将音频数据转换为NumPy数组
    audio_samples = np.frombuffer(b''.join(audio_data), dtype=np.int16)

    # 将音频数据转换为浮点数
    audio_data_float = librosa.util.buf_to_float(audio_samples, n_bytes=2, dtype=np.float32)

    # # 降噪
    audio_data_denoised = librosa.effects.remix(audio_data_float,
                                                intervals=librosa.effects.split(audio_data_float, top_db=20))

    # # Librosa部分：特征提取与判断
    # y = audio_samples / 32768.0  # 将int16数据归一化至-1~1之间
    # mfcc = librosa.feature.mfcc(y=y, sr=RATE)
    #
    # # 简单的能量阈值判断（实际VAD会更复杂）
    # energy = np.mean(np.abs(mfcc).flatten())  # 可以选择其他特征能量衡量方式
    # if energy > THRESHOLD:
    #     print("可能有人声")
    # else:
    #     print("可能无人声或主要是噪音")

    # 如果没有检测到人声，返回空数组
    # if len(voice_segments) == 0:
    #     voice_segments = np.array([], dtype=int)

    # 将降噪后的音频数据转换回整数
    audio_data_denoised_int = np.round(audio_data_denoised * 32767).astype(np.int16)
    return audio_data_denoised_int


def save_file(audio_data):
    # 音频数据处理
    audio_data_denoised_int = audio_data_dispose(audio_data)
    # 保存录制的音频数据
    with wave.open("output.wav", "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(audio.get_sample_size(FORMAT))
        wav_file.setframerate(RATE)
        wav_file.writeframes(audio_data_denoised_int.tobytes())


# 录制音频5秒（一次性）
def record_audio(stream):
    # 初始化音频数据列表
    audio_data = []
    print("开始录制--------------------")
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        audio_data.append(data)
    print("结束录制--------------------")
    # 音频保存为wav文件
    save_file(audio_data)
    # 音频文件转文字
    file_to_text()


# 录制音频每5秒转换文字一次
def for_record_audio(stream):
    while True:
        # 初始化音频数据列表
        audio_data = []
        print("5秒开始录制--------------------")
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            audio_data.append(data)
        print("5秒结束录制--------------------")
        # 音频保存为wav文件
        save_file(audio_data)
        # 音频文件转文字
        file_to_text()


def real_time():
    # 打开音频流
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    # 录制音频转化文字
    record_audio(stream)
    # 录制音频转化文字每5秒
    # for_record_audio(stream)
    # 关闭音频流
    stream.stop_stream()
    stream.close()
    # 关闭pyaudio
    audio.terminate()


if __name__ == '__main__':
    mp3Url = "G:\\JJ\\3\\output_1.mp3"
    file_to_text(mp3Url)

