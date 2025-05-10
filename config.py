# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

ROOT_DIR_WIN = Path(__file__).parent.resolve()


# 获取程序执行目录
def _get_executable_path():
    if getattr(sys, 'frozen', False):
        # 如果程序是被“冻结”打包的，使用这个路径
        return Path(sys.executable).parent.as_posix()
    else:
        return Path(__file__).parent.parent.parent.as_posix()


# 程序根目录
ROOT_DIR = _get_executable_path()

_root_path = Path(ROOT_DIR)

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

api_host = 9527

web_host = 9528

UPLOAD_DIR = "static/uploads/"

provider = "ollama"
model_name = "gemma3:12b"
api_key = 'sk-21ea07e9479d473698f7b010fd98ae70'
pexels_api_keys = "AQanz5J1ptLpe8EzANVz4fFN9R0friFxQLnvzpTjTLFbwKjpR3eL6XLA"
pixabay_api_keys = ""
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
    "large-v3"
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
