import sys
from pathlib import Path


# 获取程序执行目录
def _get_executable_path():
    if getattr(sys, 'frozen', False):
        # 如果程序是被“冻结”打包的，使用这个路径
        return Path(sys.executable).parent.as_posix()
    else:
        return Path(__file__).parent.parent.parent.as_posix()


ROOT_DIR_WIN = Path(__file__).parent.resolve()

# 程序根目录
ROOT_DIR = _get_executable_path()
_root_path = Path(ROOT_DIR)

api_host = 9527
web_host = 9528

UPLOAD_DIR = "static/uploads/"
source_videos_dir = "static/source_videos/"
source_audios_dir = "static/source_timbre/"

llm_model = 'ollama'
model_name = 'gemma3:12b'
llm_key = '1111'

video_type = 'pexels'
video_api_keys = 'AQanz5J1ptLpe8EzANVz4fFN9R0friFxQLnvzpTjTLFbwKjpR3eL6XLA'
# video_api_keys = "AQanz5J1ptLpe8EzANVz4fFN9R0friFxQLnvzpTjTLFbwKjpR3eL6XLA"
