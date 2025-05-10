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


# 获取文件名称(有后缀)
def get_file_name(file_path):
    return os.path.basename(file_path)


# 获取文件名称(无后缀)
def get_file_name_no_suffix(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


# 获取文件后缀
def get_file_suffix(file_path):
    return os.path.splitext(os.path.basename(file_path))[1]


# 文件夹添加文件
def join_suffix(folder, file_url):
    return os.path.join(folder, file_url)


# 删除文件
def del_file(file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 删除文件
        os.remove(file_path)


# 保存文本到文件
def save_text_file(content):
    file_name = "subtitle.srt"
    # Windows系统中"C盘/下载"文件夹的通用路径
    download_path = os.path.join('C:\\Users', os.getlogin(), 'Downloads')
    # 指定保存的文件路径
    file_path = os.path.join(download_path, file_name)
    # 将字幕内容写入到文件
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    return f"字幕文件已保存至: {file_path}"


# 读取文件内容
def read_text_file(file):
    if file is None:
        return ""
    with open(file.name, "r", encoding="utf-8") as f:
        content = f.read()
    return content


# 获取文件夹下所有文件名称
def get_folder_file_name(operate_folder):
    # 确保文件夹存在
    if not os.path.exists(operate_folder):
        os.makedirs(operate_folder)
    filenames = []
    # 遍历文件夹中的每个文件
    for file_path in operate_folder.iterdir():
        # 只处理文件，跳过子目录
        if file_path.is_file():
            # 去除文件扩展名并将结果添加到列表
            # filenames.append(file_path.stem)
            # 保留文件扩展名并将结果添加到列表
            filenames.append(file_path.name)
    return filenames


# 获取下载文件夹地址
def get_download_folder():
    if os.name == 'nt':  # Windows系统
        download_folder = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
    elif os.name == 'posix':  # macOS和Linux系统
        download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        raise OSError("Unsupported operating system")
    return download_folder + "/"


# 打开文件夹
def open_folder(open_path):
    # 获取下载文件夹地址
    if not open_path:
        open_path = get_download_folder()
    subprocess.run(['explorer', open_path])


# 判断文件和文件夹是否存在
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


def seconds_to_hms(seconds):
    """将秒数转换为 HH:MM:SS 格式"""
    seconds = int(round(float(seconds)))  # 处理浮点数和四舍五入
    hours = seconds // 3600
    remainder = seconds % 3600
    minutes = remainder // 60
    seconds = remainder % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
