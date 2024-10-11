import ffmpeg
import os
import subprocess
from util import file_util, tools, config
from pathlib import Path
import time
import textwrap
import sys


# 获取视频信息
def get_info(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    print(video_stream)
    width = int(video_stream['width'])
    print(width)
    height = int(video_stream['height'])
    print(height)


# 调整视频分辨率
def change_resolution(input_video_path, output_video_path):
    width, height = 640, 480
    stream = ffmpeg.input(input_video_path)
    stream = ffmpeg.filter(stream, 'scale', width, height)
    stream = ffmpeg.output(stream, output_video_path)
    ffmpeg.run(stream)


def speed_video(input_video_path, output_video_path):
    # 假设我们想要将视频速度加快到原来的2倍
    speed = 0.5
    # speed_factor = 0.5  # 减速因子，0.5 表示减速到原来的一半速度
    (
        ffmpeg
        .input(input_video_path)
        .filter('setpts', f'PTS-STARTPTS/{speed}')  # 减速视频
        .output(output_video_path, vcodec='libx264', acodec='aac', ar=44100)  # 重新编码视频和音频
        .run()
    )


# 视频剪辑
def clip_video(input_path, t_start, t_end, output_video_path):
    stream = ffmpeg.input(input_path, ss=t_start, t=t_end)
    stream = ffmpeg.output(stream, output_video_path)
    ffmpeg.run(stream)


# 视频拼接    合并相同格式的多个视频或相同格式的多个音频
def stitch_video(video1, video2, output_video_path):
    v1 = ffmpeg.input(video1)
    v2 = ffmpeg.input(video2)
    ffmpeg.concat(v1, v2).output(output_video_path).run()


# 提取音频
def get_audio(input_path, audio_suffix, output_path):
    if file_util.check_output_path(output_path):
        output_path = file_util.join_suffix(output_path, audio_suffix)
    else:
        output_path = file_util.join_suffix(file_util.get_download_folder(),
                                            file_util.set_suffix(input_path, audio_suffix))
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(stream.audio, output_path, format=audio_suffix)
    ffmpeg.run(stream)
    return "音频提取成功，下载地址为： " + output_path


# 提取视频
def get_video(input_path, video_suffix, output_path):
    if file_util.check_output_path(output_path):
        output_path = file_util.join_suffix(output_path, video_suffix)
    else:
        output_path = file_util.join_suffix(file_util.get_download_folder(),
                                            file_util.set_suffix(input_path, video_suffix))
    stream = ffmpeg.input(input_path)
    stream = ffmpeg.output(stream.video, output_path, format=video_suffix, vcodec='libx264', crf=23)
    ffmpeg.run(stream)
    return "视频提取成功，下载地址为： " + output_path


# 添加音频
def add_audio(input_path, input_audio_path, output_path):
    video_suffix = os.path.splitext(os.path.basename(input_path))[1]
    if file_util.check_output_path(output_path):
        output_path = file_util.join_suffix(output_path, video_suffix)
    else:
        output_path = file_util.join_suffix(file_util.get_download_folder(),
                                            file_util.set_suffix(input_path, video_suffix))
    video_stream = ffmpeg.input(input_path)
    audio_stream = ffmpeg.input(input_audio_path)
    stream = ffmpeg.output(video_stream, audio_stream.audio, output_path)
    ffmpeg.run(stream)


# 转换视频格式
def change_format(input_video_path, output_video_path, output_format):
    """
    Convert a video or audio file to a different format.

    Args:
        input_video_path (str): Path to the input file.
        output_video_path (str): Path where the converted file will be saved.
        output_format (str): Target format for the converted file.

    Note:
        Common video formats include: 'mp4', 'avi', 'mkv', 'flv', 'webm', etc.
        Common audio formats include: 'mp3', 'aac', 'wav', 'ogg', etc.

    This function does not list all available formats directly, but relies on FFmpeg's
    support for formats. FFmpeg's support can vary based on its compilation options
    and installed codecs
    """
    stream = ffmpeg.input(input_video_path)
    stream = ffmpeg.output(stream, output_video_path, format=output_format)
    ffmpeg.run(stream)


# 设置封面图
# def set_cover(input_video_path):
#     thumbnail_path = 'D:/opt/3.jpg'  # 如果你想使用特定的图片作为封面，可以指定这个文件
#
#     # 提取第一帧作为封面
#     (
#         ffmpeg
#         .input(input_video_path)
#         .output(thumbnail_path, vframes=1, format='jpg')
#         .run()
#     )


# 获取封面图
def get_cover(input_video_path, output_folder):
    # 指定要截取的帧的时间戳（秒），例如：第10秒
    frame_time = 10
    # 使用ffmpeg.input加载视频，然后指定-ss选项来选择开始时间，
    # 注意：将-ss放在-i之前（作为输入选项）会更快地定位到指定帧，
    # 因为FFmpeg会跳过之前的帧。
    # 然后使用-frames:v 1选项来确保只输出一帧，
    # 最后用-vf "select=eq(pict_type\,I)"来确保选择的是关键帧（I帧），
    # 但实际上，如果只想截取指定时间的一帧，这一步不是必需的。
    output_folder = 'D:/zzz/output_frame.png'
    (
        ffmpeg
        .input(input_video_path, ss=frame_time)
        .output(output_folder, vframes=1)
        .run()
    )


# 获取指定时间每一秒的图片
def get_cover_for(input_path):
    # 输出图片的基本文件名和目录
    output_dir = 'D:/zzz'
    # os.makedirs(output_dir, exist_ok=True)
    output_base = os.path.join(output_dir, 'frame_')

    # 指定开始和结束时间（秒）
    start_time = 10
    end_time = 20

    # 循环每一秒
    for time in range(start_time, end_time + 1):
        # 输出的图片文件路径，包含时间戳
        output_image = f"{output_base}{time:02d}.png"

        # 使用ffmpeg.input加载视频，设置ss为当前时间，vframes为1来只截取一帧
        (
            ffmpeg
            .input(input_path, ss=time, t=1)  # ss设置起始时间，t=1限制只处理一秒内的帧
            .output(output_image, vframes=1)
            .run()
        )


# 从视频制作gif
def get_gif(input_path):
    # 输出的GIF文件路径
    output_gif = 'D:/zzz/output.gif'

    # 设置GIF的起始时间（秒）和持续时间（秒）
    start_time = 10  # 从视频的第10秒开始
    duration = 5  # 持续时间5秒
    (
        ffmpeg
        .input(input_path, ss=start_time)
        .output(output_gif, vcodec='gif', t=duration)
        .run()
    )


# 截取音视频片段(每5秒)  'output_segment'片段长度 秒
def split_video_into_segments(input_video, segment_length, output_prefix):
    """
    根据每个片段的长度裁剪视频，并生成多个输出文件。
    """
    # 获取输入文件的持续时间
    probe = ffmpeg.probe(input_video)
    total_duration = float(probe['format']['duration'])
    # 计算需要拆分的文件数量（向上取整）
    num_segments = int(total_duration // segment_length) + (1 if total_duration % segment_length > 0 else 0)

    # 初始化起始时间
    start_time = 0

    # 循环处理每个片段
    for i in range(num_segments):
        # 计算结束时间（但不超过视频总时长）
        end_time = min(start_time + segment_length, total_duration)
        # 构造输出文件名
        output_filename = f"{output_prefix}_{i:02d}.mp4"
        # 裁剪视频片段
        (
            ffmpeg
            .input(input_video, ss=start_time)
            .output(output_filename, vcodec='copy', acodec='copy', t=end_time - start_time)
            .run()
        )
        # 更新起始时间
        start_time += segment_length


# 遍历文件夹下所有文件
def beach():
    file = f'G:\\video\\m'

    for root, dirs, files in os.walk(file):
        for file in files:
            path = os.path.join(root, file)
            # video_to_audio(path, path[:-1]+'3')
            # 提取音频: -vn表示去掉视频，-c:a copy表示不改变音频编码，直接拷贝。
            # os.system("ffmpeg -i " + path + " -vn -c:a copy "+path[:-4]+".aac")
            # 下面是 mp4 转 webm 的写法。
            os.system("ffmpeg -i " + path + " -c copy " + path[:-4] + ".mp3")
            print(path[:-1] + '3')
    pass


# 添加字幕(暂不能用，)
# ffmpeg中字幕处理的滤镜有两个subtitles和drawtext。
# 1、要想正确使用subtitles滤镜，编译ffmpeg时需要添加--enable-libass --enable-filter=subtitles配置参数，同时引入libass库。同时由于libass库又引用了freetype,fribidi外部库所以还需要同时编译这两个库，此外
# libass库根据操作系统的不同还引入不同的外部库，比如mac os系统则引入了CoreText.framework库,Linux则引入了fontconfig库，windows系统则引入了DirectWrite，或者添加--disable-require-system-font-provider
# 代表不使用这些系统的库
# 2、要想正确使用drawtext滤镜，编译ffmpeg时需要添加--enable-filter=drawtext同时要引入freetype和fribidi外部库
# 3、所以libass和drawtext滤镜从本质上看都是调用freetype生成一张图片，然后再将图片和视频融合
# 与libass库字幕处理相关的三个库：
# 1、text shaper相关：用来定义字体形状相关，fribidi和HarfBuzz两个库，其中fribidi速度较快，与字体库形状无关的一个库，libass默认，故HarfBuzz可以选择不编译
# 2、字体库相关：CoreText(ios/mac)；fontconfig(linux/android/ios/mac);DirectWrite(windows)，用来创建字体。
# 3、freetype：用于将字符串按照前面指定的字体以及字体形状渲染为字体图像(RGB格式，备注：它还可以将RGB格式最终输出为PNG，则需要编译libpng库)

# def add_subtitle(input_video_path, input_subtitle_path, output_video):
#     input_video_path = r"D:/abm.mp4"  # 使用原始字符串避免转义问题
#     input_subtitle_path = r"D:/jgl.srt"
#     output_video = r"D:/output.mp4"
#     # 使用 ffmpeg 添加字幕，并指定字幕样式
#     subtitle_filter = f'subtitles="{input_subtitle_path}"'
#
#     # 构建 ffmpeg 命令
#     command = [
#         'ffmpeg',
#         '-y',  # 自动覆盖输出文件
#         '-i', input_video_path,
#         '-vf',
#         f'{subtitle_filter}',
#         # f'{subtitle_filter}:force_style="FontName=Arial; FontSize=24; PrimaryColour=&H00FFFFFF; BackColour=&H00000000; OutlineColour=&H00000000; Outline=2"',
#         '-c:v', 'libx264',  # 使用 x264 编解码器重新编码视频
#         '-threads', '2',  # 使用多线程加速处理
#         output_video
#     ]
#
#     # 执行命令
#     process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#
#     # 检查命令是否执行成功
#     if process.returncode != 0:
#         print("Error:", process.stderr)
#     else:
#         print("Subtitle added successfully!")

def add_subtitle(video_path, subtitle_path, maxlen=30):
    output_video = file_util.get_download_folder()
    name = "abm"
    try:
        cmd = [config.FFMPEG_BIN, "-hide_banner", "-ignore_unknown"]
        cmd += [
            '-y',
            '-i',
            os.path.normpath(video_path)
        ]
        # if not self.is_soft or not self.language:
        # 硬字幕
        sub_list = tools.get_subtitle_from_srt(subtitle_path)
        # 将srt文件写入缓存并获取url
        text = ""
        for i, it in enumerate(sub_list):
            it['text'] = textwrap.fill(it['text'], maxlen, replace_whitespace=False).strip()
            text += f"{it['line']}\n{it['time']}\n{it['text'].strip()}\n\n"
        srtfile = config.TEMP_HOME + f"/srt{time.time()}.srt"
        with Path(srtfile).open('w', encoding='utf-8') as f:
            f.write(text)
            f.flush()
        # 转为ass字幕文件
        assfile = tools.set_ass_font(srtfile)
        os.chdir(config.TEMP_HOME)
        cmd += [
            '-c:v',
            'libx264',
            '-vf',
            f"subtitles={os.path.basename(assfile)}",
            '-crf',
            f'{config.settings["crf"]}',
            '-preset',
            config.settings['preset']
        ]
        # else:
        #     # 软字幕
        #     os.chdir(self.folder)
        #     subtitle_language = translator.get_subtitle_code(
        #         show_target=self.language)
        #     cmd += [
        #         '-i',
        #         os.path.basename(srt),
        #         '-c:v',
        #         'copy' if Path(info['video']).suffix.lower() == '.mp4' else 'libx264',
        #         "-c:s",
        #         "mov_text",
        #         "-metadata:s:s:0",
        #         f"language={subtitle_language}"
        #     ]
        cmd.append(output_video + f'/{name}.mp4')
        subprocess.run(cmd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       encoding="utf-8",
                       check=True,
                       text=True,
                       creationflags=0 if sys.platform != 'win32' else subprocess.CREATE_NO_WINDOW)
        return "合成成功"
    except Exception as e:
        print(e)


if __name__ == '__main__':
    # 一些Python与ffmpeg音频处理的实用程序和命令:https://www.cnblogs.com/zhaoke271828/p/17007046.html
    input_video_path = "D:/abm/abm.mp4"
    input_subtitle_path = "D:/abm/abm.srt"
    # output_video = "D:/output111.mp4"
    # output_video = "D:/abm/final"
    # add_subtitle(input_video_path, input_subtitle_path, output_video)
    add_subtitle(input_video_path, input_subtitle_path, 50)
    # # get_info(input_video_path)
    # start_time = '00:00:30'
    # duration = '00:01:00'
    # audio_output = "D:/output.mp3"

    # clip_video(input_video_path, start_time, duration, output_video)
    # get_audio(input_video_path, audio_output)
    # capture_screenshots(input_video_path, start_time, 5, "D:/zzz")
    # get_cover(input_video_path, "D:/zzz")
    # get_cover_for(input_video_path)
    # get_gif(input_video_path)
    # split_video_into_segments(input_video_path, 5, 'D:/zzz/output_segment')
    # speed_video(input_video_path, 'D:/zzz/output_.mp4')
    # change_format(input_video_path, 'D:/zzz/outputgg.avi', "avi")
    # set_cover(input_video_path)
