import os
import subprocess
from util.file_util import get_download_folder, get_file_name, get_file_suffix, get_file_name_no_suffix, set_ass_font, \
    del_file
import config
from pathlib import Path
import sys
import json


# 设置封面
def set_video_cover(input_video, cover_image):
    output_path = get_download_folder() + get_file_name_no_suffix(input_video) + "(封面)" + get_file_suffix(input_video)
    command = [
        '-i', input_video,  # 输入视频文件
        '-i', cover_image,  # 封面图片文件
        '-map', '0',  # 映射第一个输入的所有流（视频和音频）
        '-map', '1',  # 映射第二个输入（封面图片）
        '-c', 'copy',  # 复制所有流，不重新编码
        '-disposition:v:0', 'default',  # 设置第一个视频流为默认显示
        '-disposition:v:1', 'attached_pic',  # 设置封面图片为附加图片
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)
    return "封面设置成功，文件地址为：" + output_path


# 获取指定秒的第一帧
def extract_frame(input_video, time_ss):
    output_image_path = get_download_folder() + get_file_name_no_suffix(input_video) + "(图).png"

    command = [
        '-i', input_video,  # 输入视频文件
        '-ss', time_ss,  # 指定开始时间（HH:MM:SS格式）
        '-vframes', '1',  # 只提取一帧
        output_image_path  # 输出图像文件
    ]
    run_ffmpeg_cmd(command)
    return "图片提取成功"


# 获取指定时间段内每秒的第一帧
def extract_frames(input_video_path, output_dir, start_time, end_time):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 计算总帧数
    total_seconds = int(end_time.split(':')[-1]) - int(start_time.split(':')[-1])

    # 构建ffmpeg命令
    for i in range(total_seconds + 1):
        current_time = f"{int(start_time.split(':')[0]):02d}:{int(start_time.split(':')[1]):02d}:{int(start_time.split(':')[2]) + i:02d}"
        output_image_path = os.path.join(output_dir, f"frame_{i + 1:04d}.jpg")

        command = [
            '-i', input_video_path,  # 输入视频文件
            '-ss', current_time,  # 指定开始时间（HH:MM:SS格式）
            '-vframes', '1',  # 只提取一帧
            output_image_path  # 输出图像文件
        ]
        run_ffmpeg_cmd(command)


# 生成gif文件
def video_to_gif(input_video, start_time=None, duration=None, fps=10, scale='320:-1'):
    # 可选参数
    # input_video_path = 'path/to/your/input_video.mp4'
    # start_time = '00:00:05'  # 开始时间（HH:MM:SS格式），例如从第5秒开始
    # duration = '00:00:10'  # 持续时间（HH:MM:SS格式），例如10秒
    # fps = 10  # 帧率，每秒10帧
    # scale = '320:-1'  # 缩放比例，宽度320像素，高度按比例缩放
    output_gif_path = get_download_folder() + get_file_name_no_suffix(input_video) + ".gif"
    command = [
        '-i', input_video,  # 输入视频文件
    ]
    if start_time:
        command.extend(['-ss', start_time])  # 指定开始时间（可选）

    if duration:
        command.extend(['-t', duration])  # 指定持续时间（可选）

    if scale:
        command.extend(['-vf', f'scale={scale}'])  # 指定缩放比例（可选）
    else:
        command.extend(['-vf', 'fps=' + str(fps)])  # 设置帧率

    command.extend([
        '-pix_fmt', 'rgb24',  # 设置像素格式
        output_gif_path  # 输出GIF文件
    ])
    run_ffmpeg_cmd(command)


# 按时间间隔分割成多个视频
def extract_video_clips(input_video_path, output_dir, interval=5):
    # # 示例调用
    # input_video_path：视频url
    # output_directory：输出片段目录
    # interval： 时间间隔（秒）
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取视频的总时长
    duration_command = [
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_video_path
    ]
    result = run_ffprobe_cmd(duration_command)
    total_duration = float(result.stdout.strip())

    # 计算需要截取的片段数量
    num_clips = int(total_duration // interval)

    # 构建并执行命令
    for i in range(num_clips):
        start_time = i * interval
        clip_output_path = os.path.join(output_dir, f'clip_{i + 1:04d}.mp4')

        command = [
            '-i', input_video_path,  # 输入视频文件
            '-ss', str(start_time),  # 开始时间
            '-t', str(interval),  # 持续时间
            '-vsync', '0',  # 确保不跳过帧
            '-copyts',  # 复制时间戳
            '-avoid_negative_ts', 'make_zero',  # 避免负时间戳
            '-c:v', 'libx264',  # 重新编码视频流
            '-c:a', 'aac',  # 重新编码音频流
            clip_output_path  # 输出文件
        ]
        run_ffmpeg_cmd(command)


# 获取视频信息
def get_info(video_path):
    video_info = ""
    command = [
        '-v', 'quiet',  # 设置为安静模式，不打印任何信息到控制台
        '-print_format', 'json',  # 输出格式设置为JSON
        '-show_format',  # 显示容器格式信息
        '-show_streams',  # 显示所有流的信息
        video_path
    ]
    # 将结果从字符串转换成JSON对象
    info = json.loads(run_ffprobe_cmd(command).stdout)
    # 获取格式信息
    format_info = info.get('format', {})
    filename = format_info.get('filename')
    duration = float(format_info.get('duration', 0))
    overall_bitrate = format_info.get('bit_rate')

    video_info += f"文件名: {get_file_name(filename)}\n"
    video_info += f"时长: {duration:.2f}秒\n"
    if overall_bitrate:
        video_info += f"总比特率: {int(overall_bitrate) / 1000:.2f} kbps\n"
    # 遍历流信息，找到视频流
    for stream in info.get('streams', []):
        if stream['codec_type'] == 'video':
            codec_name = stream.get('codec_name')
            width = stream.get('width')
            height = stream.get('height')
            avg_frame_rate = stream.get('avg_frame_rate')
            bit_rate = stream.get('bit_rate')

            # 计算帧率
            if avg_frame_rate:
                frame_rate = eval(avg_frame_rate)  # 将分数形式的字符串转换为浮点数
            else:
                frame_rate = None
            # 打印视频相关信息
            video_info += f"视频编解码器: {codec_name}\n"
            video_info += f"分辨率: {width}x{height}\n"
            if frame_rate is not None:
                video_info += f"帧率: {frame_rate:.2f} fps\n"
            if bit_rate:
                video_info += f"比特率: {int(bit_rate) / 1000:.2f} kbps\n"
            break  # 只处理第一个视频流
    return video_info


# 提取音频
def get_audio(video_path, audio_type=".mp3"):
    audio_output_path = get_file_name_no_suffix(video_path) + "." + audio_type
    command = [
        '-i', video_path,  # 输入文件
        '-q:a', '0',  # 音频质量（0是最好的）
        '-map', 'a',  # 只选择音频流
        audio_output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)
    return "音频提取成功，文件地址为：" + audio_output_path


# 提取视频
def get_video(video_path, video_type="mp4"):
    output_path = get_file_name_no_suffix(video_path) + "(无音频)." + video_type
    command = [
        '-i', video_path,  # 输入文件
        '-c:v', 'copy',  # 复制视频编码，不进行重新编码
        '-an',  # 不包含音频
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)
    return "视频提取成功，文件地址为：" + output_path


# # 添加音频
def add_audio_to_video(video_path, audio_path):
    output_path = get_file_name_no_suffix(video_path) + "（合并音频）" + get_file_suffix(video_path)
    command = [
        '-i', video_path,  # 输入视频文件
        '-i', audio_path,  # 输入音频文件
        '-c:v', 'copy',  # 复制视频流，不重新编码
        '-c:a', 'aac',  # 使用AAC编码器编码音频
        '-map', '0:v:0',  # 映射第一个输入的第一个视频流
        '-map', '1:a:0',  # 映射第二个输入的第一个音频流
        '-shortest',  # 使输出文件长度与最短的输入文件相同
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)
    return "音频添加成功，文件地址为：" + output_path


# 音量调整
def adjust_audio_volume(input_video, volume_factor):
    output_path = get_download_folder() + get_file_name_no_suffix(input_video) + "(音量)" + get_file_suffix(input_video)

    # volume_factor：1.5表示将音量提高50%，0.5表示将音量降低50%
    command = [
        '-i', input_video,  # 输入视频文件
        '-filter_complex', f'[0:a]volume={volume_factor}[a]',  # 应用音量调整滤镜
        '-map', '0:v:0',  # 映射第一个输入的第一个视频流
        '-map', '[a]',  # 映射经过处理后的音频流
        '-c:v', 'copy',  # 复制视频流，不重新编码
        '-c:a', 'aac',  # 使用AAC编码器编码音频
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)
    return "操作成功，文件地址为：" + output_path

# 调整视频分辨率
def change_resolution(input_video, width, height):
    # 480p (标清, SD)
    # 分辨率: 640x480
    # 宽高比: 4:3 或 16:9（取决于内容）
    # 576p (PAL 标清, SD)
    # 分辨率: 720x576
    # 宽高比: 4:3 或 16:9
    # 720p (高清, HD)
    # 分辨率: 1280x720
    # 宽高比: 16:9
    # 1080p (全高清, Full HD)
    # 分辨率: 1920x1080
    # 宽高比: 16:9
    # 1440p (2K, QHD)
    # 分辨率: 2560x1440
    # 宽高比: 16:9
    # 2160p (4K UHD)
    # 分辨率: 3840x2160
    # 宽高比: 16:9
    # 4320p (8K UHD)
    # 分辨率: 7680x4320
    # 宽高比: 16:9
    output_path = get_download_folder() + get_file_name_no_suffix(input_video) + "(分辨率)" + get_file_suffix(
        input_video)

    command = [
        '-i', input_video,  # 输入文件
        '-vf', f'scale={width}:{height}',  # 视频过滤器：调整分辨率
        '-c:a', 'copy',  # 复制音频流，不重新编码
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)
    return "分辨率调整成功，文件地址为：" + output_path


# 控制速度
def speed_video(input_video, speed_factor):
    output_path = get_download_folder() + get_file_name_no_suffix(input_video) + "(速度)" + get_file_suffix(input_video)

    # atempo滤镜支持的最大范围是0.5到2.0
    # speed_factor 减慢0.5倍或加快2倍
    command = [
        '-i', input_video,  # 输入文件
        '-filter_complex', f'[0:v]setpts={1 / speed_factor}*PTS[v];[0:a]atempo={speed_factor}[a]',  # 设置视频和音频的速度
        '-map', '[v]',  # 映射视频流
        '-map', '[a]',  # 映射音频流
        '-c:v', 'libx264',  # 使用H.264编码器重新编码视频
        '-c:a', 'aac',  # 使用AAC编码器重新编码音频
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)


# 视频格式转化
def convert_video_format(input_path, video_type):
    # 获取原始视频的信息
    command = [
        '-v', 'quiet',  # 设置为安静模式，不打印任何信息到控制台
        '-print_format', 'json',  # 输出格式设置为JSON
        '-show_format',  # 显示容器格式信息
        '-show_streams',  # 显示所有流的信息
        input_path
    ]
    # 将结果从字符串转换成JSON对象
    probe = json.loads(run_ffprobe_cmd(command).stdout)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

    avg_bitrate = int(float(video_stream.get('bit_rate', 0)) / 1000)  # 转换为Kbps

    output_path = get_download_folder() + get_file_name_no_suffix(
        input_path) + "." + video_type

    command = [
        '-i', input_path,
        '-c:v', 'libx264',
        '-b:v', f'{avg_bitrate}k',  # 使用原视频的平均比特率
        # 使用CRF（恒定质量因子）：对于H.264编码器，CRF值是一个非常重要的参数，它可以在文件大小和视频质量之间提供一个很好的平衡。
        # 通常情况下，CRF的范围是0-51，其中0表示无损，23是默认值，51是最差的质量。一般建议使用18-23之间的值
        '-crf', '23',
        '-c:a', 'aac',
        output_path
    ]

    # 根据输出格式调整编解码器
    if video_type == 'webm':
        command[command.index('-c:v') + 1] = 'libvpx-vp9'
        command[command.index('-c:a') + 1] = 'libopus'
    elif video_type == 'avi':
        command[command.index('-c:v') + 1] = 'libxvid'
        command[command.index('-c:a') + 1] = 'mp3'
    elif video_type == 'mkv':
        command[command.index('-c:v') + 1] = 'copy'
        command[command.index('-c:a') + 1] = 'copy'
    elif video_type == 'flv':
        command[command.index('-c:v') + 1] = 'libx264'
        command[command.index('-c:a') + 1] = 'aac'
    run_ffmpeg_cmd(command)
    return "视频格式转化成功，文件地址为：" + output_path


# 合并视频
def concatenate_videos_with_filter(video_paths, output_path):
    # 构建filter_complex选项
    filter_complex = f'concat=n={len(video_paths)}:v=1:a=1 [v] [a]'

    command = []

    for video in video_paths:
        command.extend(['-i', video])

    command.extend([
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264',  # 使用H.264编码器
        '-c:a', 'aac',  # 使用AAC编码器
        output_path  # 输出文件
    ])
    run_ffmpeg_cmd(command)
    return "视频合并成功，文件地址为：" + output_path


# 分割视频
def cut_video(input_path, start_time, end_time=None, duration=None):
    # start_time = '00:00:10'
    # 从第10秒开始，持续20秒
    # duration = '00:00:20'
    # 或者从第10秒开始，到第30秒结束
    # end_time = '00:00:30'
    output_path = get_download_folder() + get_file_name_no_suffix(
        input_path) + "(剪切)" + get_file_suffix(input_path)
    command = [
        '-i', input_path,  # 输入视频文件
        '-ss', start_time,  # 开始时间
        '-c', 'copy',  # 复制流，不重新编码
        output_path  # 输出文件
    ]

    if duration:
        command.insert(4, '-t')
        command.insert(5, duration)
    elif end_time:
        command.insert(4, '-to')
        command.insert(5, end_time)
    run_ffmpeg_cmd(command)
    return "视频剪切完成，文件地址为：" + output_path


# 视频添加字幕
def add_subtitle(video_path, subtitle_content, subtitle_type, fontsize=20):
    try:
        cmd = ["-hide_banner",
               "-ignore_unknown",
               '-y',
               '-i',
               os.path.normpath(video_path)
               ]
        output_video = get_download_folder()
        # 获取文件名称
        name = get_file_name_no_suffix(video_path)
        srt_file = f'{name}.srt'
        # 保存str文件
        with open(srt_file, "w", encoding="utf-8") as file:
            file.write(subtitle_content)

        if subtitle_type:
            # 软字幕
            cmd += [
                '-i', srt_file,
                '-c:v', 'copy' if Path(video_path).suffix.lower() == '.mp4' else 'libx264',
                '-c:s', 'mov_text',
                '-metadata:s:s:0', 'language=chi'  # 设置字幕语言，例如中文
            ]
        else:
            # 硬字幕
            ass_file = f'{name}.ass'
            # 字幕文件SRT转ASS
            str_to_ass(srt_file, ass_file)
            # 设置ass字体格式
            set_ass_font(ass_file, fontsize)
            cmd += [
                '-c:v', 'libx264',
                '-vf', f"subtitles={ass_file}",
                '-crf', '13',
                '-preset', "slow"
            ]
        output_video = output_video + f'{name}.mp4'
        cmd.append(output_video)
        run_ffmpeg_cmd(cmd)
        del_file(srt_file)
        del_file(ass_file)
        return f"合成字幕成功,文件地址为：{output_video}"
    except Exception as e:
        print(e)


# 字幕文件SRT转ASS
def str_to_ass(srt_file, ass_file):
    run_ffmpeg_cmd(['-hide_banner', '-ignore_unknown',
                    '-y',
                    '-i',
                    f'{srt_file}',
                    f'{ass_file}'])


# cmd执行ffmpeg命令
def run_ffmpeg_cmd(cmd):
    try:
        command = [
            config.FFMPEG_BIN
        ]
        # 检查ffmpeg是否支持CUDA
        # if check_cuda_support():
        #     command.extend(['-hwaccel', 'cuda'])
        command.extend(cmd)
        print(command)
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                encoding="utf-8",
                                check=True,
                                creationflags=0 if sys.platform != 'win32' else subprocess.CREATE_NO_WINDOW
                                )
        print(result)
        return result
    except subprocess.CalledProcessError as e:
        print("An error occurred while running the command.")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")


def check_cuda_support():
    # 检查ffmpeg是否支持CUDA
    cmd = ['ffmpeg', '-hwaccels']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result and 'cuda' in result.stdout.lower():
        return True
    return False


# cmd执行ffprobe命令
def run_ffprobe_cmd(cmd):
    try:
        command = [
            config.FFPROBE_BIN
        ]
        command.extend(cmd)
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                encoding="utf-8",
                                check=True,
                                creationflags=0 if sys.platform != 'win32' else subprocess.CREATE_NO_WINDOW
                                )
        print(result)
        return result
    except subprocess.CalledProcessError as e:
        print("An error occurred while running the command.")
        print(f"Command: {e.cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")


if __name__ == '__main__':
    # 一些Python与ffmpeg音频处理的实用程序和命令:https://www.cnblogs.com/zhaoke271828/p/17007046.html
    input_video_path = "D:/abm/abm.mp4"
    output_video = "D:/output113.mp4"
    audio_output = "D:/abm.mp3"
    cover_image_path = "D:/opt/21.jpg"
    # output_video = "D:/abm/final"
    # input_subtitle_path = "D:/abm/abm.srt"
    # add_subtitle(input_video_path, input_subtitle_path, 50)

    # get_info(input_video_path)
    # get_audio(input_video_path, audio_output)
    # get_video(input_video_path, output_video)
    # change_resolution(input_video_path, output_video, 640, 480)
    # speed_video(input_video_path, output_video, 1.5)
    # add_audio_to_video(input_video_path, audio_output, output_video)
    # adjust_audio_volume(input_video_path, output_video, 0.5)
    convert_video_format(input_video_path, "D:/output111.avi")

    # 调用函数拼接视频
    # video_paths = [
    #     'D:/output111.mp4',
    #     'D:/output112.mp4'
    # ]
    # concatenate_videos_with_filter(video_paths, output_video)

    start_time = '00:00:10'
    # 从第10秒开始，持续20秒
    duration = '00:00:10'
    # 或者从第10秒开始，到第25秒结束
    end_time = '00:00:25'

    # 调用函数切割视频
    # cut_video(input_video_path, output_video, start_time, duration=duration)  # 使用持续时间
    # 或者
    # cut_video(input_video_path, output_video, start_time, end_time=end_time)  # 使用结束时间

    # set_video_cover(input_video_path, cover_image_path, output_video)
    time_in_hhmmss = '00:00:10'  # 提取第10秒的第一帧
    # extract_frame(input_video_path, "D:/21.jpg", time_in_hhmmss)
    # extract_frames(input_video_path, "D:/333", start_time, end_time)

    # video_to_gif(input_video_path, "D:/output.gif", start_time=start_time, duration=duration)
    # extract_video_clips(input_video_path, "D:/333")
