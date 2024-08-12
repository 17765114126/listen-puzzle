import sounddevice as sd
import numpy as np
import threading
from data import use_fast_whisper


class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.recording_thread = None
        self.frames = []

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.frames = []
            fs = 44100  # 采样率
            self.recording_thread = threading.Thread(target=self.record_audio, args=(fs,))
            self.recording_thread.start()
            print("开始录音...")

    def record_audio(self, fs):
        with sd.InputStream(samplerate=fs, channels=2,
                            callback=lambda indata, frames, time, status: self.frames.append(indata.copy())):
            while self.recording:
                pass  # 录音是实时的，无需模拟时长增加

    def stop_recording(self):
        self.recording = False
        if self.recording_thread is not None:
            self.recording_thread.join()
            print("录音已停止。")
            # filename = 'output.wav'
            data = np.concatenate(self.frames, axis=0)
            # 转换为numpy数组
            audio_data = np.frombuffer(data, dtype=np.float32).flatten()
            recognized_text = use_fast_whisper.transcription(audio_data, None)
            print("转录文本" + recognized_text)
            # with sf.SoundFile(filename, mode='w', samplerate=44100, channels=2) as file:
            #     file.write(data)
            # print(f"录音已保存到 {filename}")


# 创建录音器实例
recorder = AudioRecorder()


def check_device():
    """录音0.01秒以检查是否有可用的录音设备"""
    try:
        # 麦克风录音参数
        SAMPLE_RATE = 16000
        CHANNELS = 1
        DURATION = 0.01  # 持续时间
        record = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
        sd.wait()  # 等待录音完成
        return True
    except Exception as e:
        print(f"Error checking devices: {e}")
        return False


def listen_for_audio(button_pressed):
    if not check_device():
        return "没有可用的录音设备。"
    """根据按钮点击控制录音"""
    if button_pressed:
        if not recorder.recording:
            recorder.start_recording()
            return "正在录音..."
        else:
            recorder.stop_recording()
            return "已停止录音."
    else:
        return "点击开始录音."
