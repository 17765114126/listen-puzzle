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


# 设置ass字体格式
def set_ass_font(ass_file, fontsize=20):
    # 打开ass文件
    with open(ass_file, 'r', encoding='utf-8') as f:
        ass_str = f.readlines()
    # 修改字幕样式
    for i, it in enumerate(ass_str):
        if it.find('Style: ') == 0:
            ass_str[
                i] = 'Style: Default,{fontname},{fontsize},{fontcolor},&HFFFFFF,{fontbordercolor},&H0,0,0,0,0,100,100,0,0,1,1,0,2,10,10,{subtitle_bottom},1'.format(
                fontname="Arial", fontsize=fontsize,
                fontcolor="&hffffff", fontbordercolor="&h000000",
                subtitle_bottom=10, )
            break

    # 写入ass文件
    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write("".join(ass_str))
    return ass_file


def seconds_to_hms(seconds):
    """将秒数转换为 HH:MM:SS 格式"""
    seconds = int(round(float(seconds)))  # 处理浮点数和四舍五入
    hours = seconds // 3600
    remainder = seconds % 3600
    minutes = remainder // 60
    seconds = remainder % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
