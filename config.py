# -*- coding: utf-8 -*-
import datetime
import json
import locale
import logging
import os
import re
import sys
import tempfile
from pathlib import Path
from queue import Queue


# 获取程序执行目录
def _get_executable_path():
    if getattr(sys, 'frozen', False):
        # 如果程序是被“冻结”打包的，使用这个路径
        return Path(sys.executable).parent.as_posix()
    else:
        return Path(__file__).parent.parent.parent.as_posix()


SYS_TMP = Path(tempfile.gettempdir()).as_posix()

# 程序根目录
ROOT_DIR = _get_executable_path()

_root_path = Path(ROOT_DIR)

_tmpname = f'tmp'
# 程序根下临时目录tmp
_temp_path = _root_path / _tmpname
_temp_path.mkdir(parents=True, exist_ok=True)
TEMP_DIR = _temp_path.as_posix()

# 模型下载地址
MODELS_DOWNLOAD = {
    "openai": {
        "tiny.en": "https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03/tiny.en.pt",
        "tiny": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
        "base.en": "https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/base.en.pt",
        "base": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
        "small.en": "https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt",
        "small": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
        "medium.en": "https://openaipublic.azureedge.net/main/whisper/models/d7440d1dc186f76616474e0ff0b3b6b879abc9d1a4926b7adfa41db2d497ab4f/medium.en.pt",
        "medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
        "large-v1": "https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large-v1.pt",
        "large-v2": "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
        "large-v3": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
        "large-v3-turbo": "https://openaipublic.azureedge.net/main/whisper/models/aff26ae408abcba5fbf8813c21e62b0941638c5f6eebfb145be0c9839262a19a/large-v3-turbo.pt",
    },
    "faster": {
        "tiny": "https://github.com/jianchang512/stt/releases/download/0.0/faster-tiny.7z",
        "tiny.en": "https://github.com/jianchang512/stt/releases/download/0.0/faster-tiny.en.7z",
        "base": "https://github.com/jianchang512/stt/releases/download/0.0/faster-base.7z",
        "base.en": "https://github.com/jianchang512/stt/releases/download/0.0/faster-base.en.7z",

        "small": "https://github.com/jianchang512/stt/releases/download/0.0/faster-small.7z",
        "small.en": "https://github.com/jianchang512/stt/releases/download/0.0/faster-small.en.7z",

        "medium": "https://github.com/jianchang512/stt/releases/download/0.0/faster-medium.7z",
        "medium.en": "https://github.com/jianchang512/stt/releases/download/0.0/faster-medium.en.7z",

        "large-v1": "https://huggingface.co/spaces/mortimerme/s4/resolve/main/faster-large-v1.7z?download=true",

        "large-v2": "https://huggingface.co/spaces/mortimerme/s4/resolve/main/largev2-jieyao-dao-models.7z",

        "large-v3": "https://huggingface.co/spaces/mortimerme/s4/resolve/main/faster-largev3.7z?download=true",
        "large-v3-turbo": "https://github.com/jianchang512/stt/releases/download/0.0/faster-large-v3-turbo.7z",

        "distil-whisper-small.en": "https://github.com/jianchang512/stt/releases/download/0.0/distil-whisper-small.en.7z",

        "distil-whisper-medium.en": "https://github.com/jianchang512/stt/releases/download/0.0/distil-whisper-medium.en.7z",

        "distil-whisper-large-v2": "https://github.com/jianchang512/stt/releases/download/0.0/distil-whisper-large-v2.7z",

        "distil-whisper-large-v3": "https://github.com/jianchang512/stt/releases/download/0.0/distil-whisper-large-v3.7z"
    }
}

FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"
# ffmpeg
if sys.platform == 'win32':
    os.environ['PATH'] = ROOT_DIR + f';{ROOT_DIR}/ffmpeg;' + os.environ['PATH']
    if Path(ROOT_DIR + '/ffmpeg/ffmpeg.exe').is_file():
        FFMPEG_BIN = ROOT_DIR + '/ffmpeg/ffmpeg.exe'
    if Path(ROOT_DIR + '/ffmpeg/ffprobe.exe').is_file():
        FFPROBE_BIN = ROOT_DIR + '/ffmpeg/ffprobe.exe'
else:
    os.environ['PATH'] = ROOT_DIR + f':{ROOT_DIR}/ffmpeg:' + os.environ['PATH']
    if Path(ROOT_DIR + '/ffmpeg/ffmpeg').is_file():
        FFMPEG_BIN = ROOT_DIR + '/ffmpeg/ffmpeg'
    if Path(ROOT_DIR + '/ffmpeg/ffprobe').is_file():
        FFPROBE_BIN = ROOT_DIR + '/ffmpeg/ffprobe'

# os.environ['QT_API'] = 'pyside6'
# os.environ['SOFT_NAME'] = 'pyvideotrans'

#####################################
resolution = [
    "4320p",
    "2160p",
    "1440p",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p"
]
# 支持的视频格式
video_type = ["mp4", "avi", "flv", "mkv", "mpeg"]
# 支持的音频格式
audio_type = ["mp3", "wav", "aac", "flac", "m4a"]
whisper_model = [
    "tiny",
    "base",
    "small",
    "medium",
    "large"
]
whisper_device = ["cpu", "cuda"]
whisper_language = [
    "auto",
    "zh",
    "en",
    "ru",
    "fr",
    "de",
    "ko",
    "ja"
]
translator_language = [
    "zh",
    "en",
    "ru",
    "fr",
    "de",
    "ko",
    "ja",
    "ar",
    "es"
]
translator_engine = [
    "bing",
    "sogou",
    "alibaba",
    "caiyun",
    "deepl",
    "ollama"
]
ollama_translate_model = "qwen"
