import argparse
import io
import os
import speech_recognition as sr
import whisper
import torch

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from sys import platform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    # The last time a recording was retreived from the queue.
    # 上次从队列中检索录制文件的时间。
    phrase_time = None
    # Current raw audio bytes.
    # 当前原始音频字节。
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    # 线程安全队列，用于从线程记录回调传递数据。
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feauture where it can detect when speech ends.
    # 我们使用语音识别器来录制我们的音频，因为它有一个很好的功能，它可以检测语音何时结束。
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold


    # Definitely do this, dynamic energy compensation lowers the energy threshold dramtically to a point where the SpeechRecognizer never stops recording.
    # 一定要这样做，动态能量补偿将能量阈值降低到语音识别器永远不会停止录制的程度。
    recorder.dynamic_energy_threshold = False

    # Important for linux users.
    # 对 Linux 用户很重要。
    # Prevents permanent application hang and crash by using the wrong Microphone
    # 防止应用程序永久挂起和使用错误的麦克风而崩溃
    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    # 加载模型
    model = args.model
    # if args.model != "large" and not args.non_english:
    #     model = model + ".en"
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    temp_file = NamedTemporaryFile().name
    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        """
        Threaded callback function to recieve audio data when recordings finish.
        线程回调函数，用于在录制完成后接收音频数据。
        audio: An AudioData containing the recorded bytes.
        audio：包含记录字节的音频数据。
        """
        # Grab the raw bytes and push it into the thread safe queue.
        # 获取原始字节并将其推送到线程安全队列中。
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # 创建一个后台线程，该线程将向我们传递原始音频字节。
    # We could do this manually but SpeechRecognizer provides a nice helper.
    # 我们可以手动执行此操作，但语音识别器提供了一个很好的帮助程序。
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    # 提示用户我们已准备就绪。
    print("Model loaded.\n")

    while True:
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            # 从队列中提取原始录制的音频。
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # 如果录制之间经过了足够的时间，则认为该短语已完成。
                # Clear the current working audio buffer to start over with the new data.
                # 清除当前工作的音频缓冲区以使用新数据重新开始。
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    last_sample = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                # 这是我们最后一次从队列中收到新的音频数据。
                phrase_time = now

                # Concatenate our current audio data with the latest audio data.
                # 将我们当前的音频数据与最新的音频数据连接起来。
                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                # Use AudioData to convert the raw data to wav data.
                # 使用音频数据将原始数据转换为 wav 数据。
                audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                # 将 wav 数据作为字节写入临时文件。
                with open(temp_file, 'w+b') as f:
                    f.write(wav_data.read())

                # Read the transcription.
                # 语音转录。指定语言,也可不指定
                result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available(),language='zh')
                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcripion.
                # 如果我们检测到录制之间有停顿，请在转录中添加一个新项目。
                # Otherwise edit the existing one.
                # 否则，请编辑现有版本。
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                # Clear the console to reprint the updated transcription.
                # 清除控制台以重新打印更新的听录。
                os.system('cls' if os.name == 'nt' else 'clear')
                print('----------------------------------')
                print(text)
                # for line in transcription:
                #     # 输出
                #     print(line)
                # Flush stdout.
                print('', end='', flush=True)

                # Infinite loops are bad for processors, must sleep.
                # 无限循环对处理器不利，必须休眠。
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()

# 需要引的包
    # pyaudio
    # SpeechRecognition
    # --extra - index - url
    # https: // download.pytorch.org / whl / cu116
    # torch
    # git + https: // github.com / openai / whisper.git