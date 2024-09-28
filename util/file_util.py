import os
import subprocess
import re
from pathlib import Path


def sanitize_title(title):
    # Only keep numbers, letters, Chinese characters, and spaces
    title = re.sub(r'[^\w\u4e00-\u9fff \d_-]', '', title)
    # Replace multiple spaces with a single space
    title = re.sub(r'\s+', ' ', title)
    return title


# 将输入路径后缀去除 添加新后缀
def set_suffix(input_path, audio_type):
    # 获取文件名（不包括扩展名）
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    # 创建输出文件路径
    return f"{base_name}.{audio_type}"


# 文件夹添加文件
def join_suffix(folder, file_url):
    return os.path.join(folder, file_url)


def get_chats():
    # 获取当前脚本所在目录，即项目根目录
    project_root = Path(__file__).resolve().parent.parent
    # 指定chats文件夹
    chats_folder = project_root / 'chats'
    # 确保 chats 文件夹存在
    if not os.path.exists(chats_folder):
        os.makedirs(chats_folder)
    # 初始化一个空列表来保存文件名
    filenames = []
    # 遍历文件夹中的每个文件
    for file_path in chats_folder.iterdir():
        # 只处理文件，跳过子目录
        if file_path.is_file():
            # 去除文件扩展名并将结果添加到列表
            file_path_stem = []
            file_path_stem.append(file_path.stem)
            file_path_stem.append("x")
            filenames.append(file_path_stem)
    return filenames


# 获取下载文件夹地址
def get_download_folder():
    if os.name == 'nt':  # Windows系统
        download_folder = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    elif os.name == 'posix':  # macOS和Linux系统
        download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        raise OSError("Unsupported operating system")
    return download_folder


# 打开文件夹
def open_folder():
    # 获取当前脚本所在的文件夹路径
    # current_folder = os.path.dirname(os.path.abspath(__file__))
    # Windows系统中"C盘/下载"文件夹的通用路径
    download_path = os.path.join('C:\\Users', os.getlogin(), 'Downloads')
    subprocess.run(['explorer', download_path])


def check_folder(target_file):
    # 分离文件路径和文件名
    folder_path, _ = os.path.split(target_file)
    # 检查文件夹是否存在,不存在返回False
    if not os.path.exists(folder_path):
        return False
    # 检查目标文件是否存在,不存在返回False
    if not os.path.exists(target_file):
        return False
    return True


def check_output_path(output_path):
    if output_path is None or output_path == "":
        # output_path为空字符串和None返回faste
        return False
    if not os.path.exists(output_path):
        # output路径 不存在，函数返回 False
        return False
    if not os.path.isdir(output_path):
        # output_path 不是一个目录，函数返回 False
        return False
    if not os.access(output_path, os.R_OK | os.W_OK):
        # output_path 不是一个目录，函数返回 False
        return False
    return True


# 保存转录结果为SRT文件
def out_srt_file(segments, output_srt_file):
    with open(output_srt_file, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            start_time = segment['start']
            end_time = segment['end']
            start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
            end_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"
            subtitle_text = segment["text"].strip()
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_str} --> {end_str}\n")
            srt_file.write(f"{subtitle_text}\n\n")


# 将segments转换为SRT格式
def segments_to_srt(segments, output_srt_file):
    with open(output_srt_file, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(segments, start=1):
            start_time = segment.start
            end_time = segment.end
            start_str = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
            end_str = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"
            subtitle_text = segment.text.strip()
            srt_file.write(f"{i}\n")
            srt_file.write(f"{start_str} --> {end_str}\n")
            srt_file.write(f"{subtitle_text}\n\n")
