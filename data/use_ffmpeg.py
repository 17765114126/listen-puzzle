import os, re, sys, json, subprocess
from data.util.file_util import get_download_folder, get_file_name, get_file_suffix, get_file_name_no_suffix, \
    del_file
import config
from pathlib import Path
from data.util import file_util


def process_video(input_path, output_path=None,
                  start_time=None, end_time=None, duration=None,
                  speed_factor=None, volume_factor=None,
                  width=None, height=None,
                  cover_image=None,
                  output_format='mp4'):
    print(speed_factor)
    print(volume_factor)
    if speed_factor is None:
        speed_factor = 1.0
    if volume_factor is None:
        volume_factor = 1.0
    """
    综合视频处理方法（剪切/调速/分辨率/音量/封面/格式转换）

    参数说明：
    - input_path: 输入文件路径
    - output_path: 输出路径（默认自动生成）
    - start_time/end_time/duration: 时间剪切参数（格式：HH:MM:SS）
    - speed_factor: 播放速度（默认1.0不变，0.5=减速一半，2.0=加速2倍）
    - volume_factor: 音量倍数（默认1.0不变）
    - width/height: 目标分辨率（默认保持原分辨率）
    - cover_image: 封面图片路径（默认不加封面）
    - output_format: 输出格式（默认mp4）
    """
    # 基础命令
    cmd = [
        'ffmpeg',
        '-hide_banner',
        '-y'  # 覆盖输出文件
    ]

    # 添加时间剪切参数
    if start_time:
        cmd.extend(['-ss', start_time])

    # 输入文件
    cmd.extend(['-i', input_path])

    # 封面图片处理
    if cover_image:
        cmd.extend(['-i', cover_image])

    # 构建滤镜链
    video_filters = []
    audio_filters = []

    # 速度调整
    if speed_factor != 1.0:
        video_filters.append(f"setpts={1 / speed_factor}*PTS")
        audio_filters.append(f"atempo={speed_factor}")

    # 分辨率调整
    if width and height:
        video_filters.append(f"scale={width}:{height}")

    # 音量调整
    if volume_factor != 1.0:
        audio_filters.append(f"volume={volume_factor}")

        # 构建滤镜链
    filter_complex = []
    need_filter = False  # 新增判断标志

    # 视频处理分支
    video_stream = '0:v'
    if speed_factor != 1.0 or (width and height):
        video_filters = []
        if speed_factor != 1.0:
            video_filters.append(f"setpts={1 / speed_factor}*PTS")
        if width and height:
            video_filters.append(f"scale={width}:{height}")
        filter_complex.append(f"[0:v]{','.join(video_filters)}[vout]")
        video_stream = "[vout]"
        need_filter = True

    # 音频处理分支
    audio_stream = '0:a'
    if speed_factor != 1.0 or volume_factor != 1.0:
        audio_filters = []
        if speed_factor != 1.0:
            audio_filters.append(f"atempo={speed_factor}")
        if volume_factor != 1.0:
            audio_filters.append(f"volume={volume_factor}")
        filter_complex.append(f"[0:a]{','.join(audio_filters)}[aout]")
        audio_stream = "[aout]"
        need_filter = True

    # 封面处理
    # if cover_image:
    #     filter_complex.append(f"[1:v]copy[cover]")
    #     need_filter = True

    # 条件添加滤镜链
    if need_filter:
        cmd.extend(['-filter_complex', ';'.join(filter_complex)])

    # 输出映射（动态调整）
    cmd += ['-map', video_stream, '-map', audio_stream]
    if cover_image:
        cmd += ['-map', '[cover]']

    # 编码参数
    codec_config = {
        'mp4': {'vcodec': 'libx264', 'acodec': 'aac'},
        'webm': {'vcodec': 'libvpx-vp9', 'acodec': 'libopus'},
        'mkv': {'vcodec': 'copy', 'acodec': 'copy'},
        'avi': {'vcodec': 'libxvid', 'acodec': 'mp3'}
    }
    config = codec_config.get(output_format, codec_config['mp4'])

    cmd.extend([
        '-c:v', config['vcodec'],
        '-c:a', config['acodec'],
        '-movflags', '+faststart',
        '-crf', '23',
        '-preset', 'fast'
    ])

    # 设置封面属性
    if cover_image:
        cmd.extend([
            '-disposition:v:0', 'default',
            '-disposition:v:1', 'attached_pic'
        ])

    # 时间参数（结束时间或持续时间）
    if duration:
        cmd.extend(['-t', duration])
    elif end_time:
        cmd.extend(['-to', end_time])

    # 输出文件
    cmd.append(output_path)

    try:
        subprocess.run(cmd, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        return f"处理失败：{e.stderr}"


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
    format = info.get('format', {})
    filename = format.get('filename')
    raw_duration = float(format.get('duration', 0))
    # overall_bitrate = format_info.get('bit_rate')
    # 转换时长格式
    try:
        duration = file_util.seconds_to_hms(raw_duration)
    except (ValueError, TypeError):
        duration = "00:00:00"  # 异常时返回默认值
    return {"filename": get_file_name(filename), "duration": f"{duration}", "format": format}


# 提取音频
def get_audio(video_path, output_path):
    command = [
        '-i', video_path,  # 输入文件
        '-q:a', '0',  # 音频质量（0是最好的）
        '-map', 'a',  # 只选择音频流
        output_path  # 输出文件
    ]
    run_ffmpeg_cmd(command)


# # 添加音频
def add_audio_to_video(video_path, audio_path, output_path):
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


def add_subtitle(video_path, subtitle_content, subtitle_type,
                 fontname="楷体", fontsize=16, fontcolor="&Hffffff",
                 fontbordercolor="&H000000", subtitle_bottom=20
                 ):
    """添加字幕到视频文件
    Args:
        video_path:  视频url
        subtitle_content: 字幕内容
        subtitle_type: 字幕类型：硬字幕 如按字母
        font_name: 支持系统已安装的任何字体
        fontsize: 字体大小
        font_color: ASS格式颜色代码，默认白色，黑色
        subtitle_bottom: 底部边距像素值
    """
    cmd = ["-hide_banner",
           "-ignore_unknown",
           '-y',
           '-i',
           os.path.normpath(video_path)
           ]
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
        set_ass_font(ass_file, fontname, fontsize, fontcolor, fontbordercolor, subtitle_bottom)
        cmd += [
            '-c:v', 'libx264',
            '-vf', f"subtitles={ass_file}",
            '-crf', '13',
            '-preset', "slow"
        ]
    output_video = config.ROOT_DIR_WIN / config.UPLOAD_DIR / f'video_add_subtitle.mp4'
    cmd.append(output_video)
    run_ffmpeg_cmd(cmd)
    del_file(srt_file)
    del_file(ass_file)
    return f'video_add_subtitle.mp4'


# 字幕文件SRT转ASS
def str_to_ass(srt_file, ass_file):
    run_ffmpeg_cmd(['-hide_banner', '-ignore_unknown',
                    '-y',
                    '-i',
                    f'{srt_file}',
                    f'{ass_file}'])


# 设置ass字体格式
def set_ass_font(ass_file, fontname, fontsize, fontcolor, fontbordercolor, subtitle_bottom):
    with open(ass_file, 'r+', encoding='utf-8') as f:
        content = f.read()

        # 使用正则表达式精准匹配样式行（包含Windows字体名空格）
        style_pattern = re.compile(r'^Style:\s*.*', flags=re.MULTILINE)
        new_style = (
            f"Style: Default,{fontname},{fontsize},"
            f"{fontcolor},&HFFFFFF,{fontbordercolor},&H0,0,0,0,0,"
            f"100,100,0,0,1,1,0,2,10,10,{subtitle_bottom},1"
        )
        updated_content = re.sub(style_pattern, new_style, content, count=1)

        f.seek(0)
        f.write(updated_content)
        f.truncate()
    return ass_file


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
    # convert_video_format(input_video_path, "D:/output111.avi")

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

    video_url = "D:\\sucai\\22.mp4"
    jpg_url = "D:\\video_sucai\\p1.jpg"
    # # 基本处理（只转格式）
    # print(process_video(video_url, output_format='avi'))
    #
    # # 加速处理+调整分辨率
    # print(process_video(video_url, speed_factor=1.5, width=1280, height=720))
    #
    # # 添加封面+剪切
    # print(process_video(video_url,
    #                     # cover_image=jpg_url,
    #                     start_time="00:01:00",
    #                     end_time="00:02:00"))

    # # 完整参数示例
    # print(process_video(video_url, output_format="mp4",
    #                     speed_factor=0.8,
    #                     volume_factor=2.0,
    #                     width=640, height=480,
    #                     start_time="00:00:30",
    #                     duration="00:01:30",
    #                     # cover_image="cover.png"
    #                     )
    #       )
    subtitle_content = """
1
00:00:00,000 --> 00:00:03,240
99推出LiveCC视频解说模型

2
00:00:03,240 --> 00:00:05,660
CC for Closed Caption

3
00:00:05,660 --> 00:00:09,279
能够模仿人类解说员对体育比赛

4
00:00:09,279 --> 00:00:12,599
The NBA playoffs are underway

5
00:00:12,599 --> 00:00:15,339
Game 1 of the Western Conference

6
00:00:15,339 --> 00:00:17,760
First round between the No. 2

7
00:00:17,760 --> 00:00:19,839
seated Houston Rockets

8
00:00:19,839 --> 00:00:21,039
小学视频

9
00:00:21,039 --> 00:00:24,859
Hey guys, today I will show you

10
00:00:24,859 --> 00:00:27,120
how to fix a water-damaged laptop

11
00:00:27,120 --> 00:00:28,679
So if you've got a laptop

12
00:00:28,679 --> 00:00:31,079
that's been accidentally spilled on

13
00:00:31,079 --> 00:00:33,560
or you've dropped it in a puddle of water

14
00:00:33,560 --> 00:00:34,920
this is what you need to do

15
00:00:34,920 --> 00:00:36,380
先上游戏的

16
00:00:36,380 --> 00:00:38,939
Hey guys, I'm going to be showing you

17
00:00:38,939 --> 00:00:41,420
what happened in 7.38c

18
00:00:41,420 --> 00:00:42,859
So the first thing that happened

19
00:00:42,859 --> 00:00:46,200
was time zone no longer manipulates

20
00:00:46,200 --> 00:00:47,719
实时解说

21
00:00:47,719 --> 00:00:51,920
实验显示LiveCC 7B Instruct模型

22
00:00:51,920 --> 00:00:54,019
在实时模式下的解说质量

23
00:00:54,019 --> 00:00:57,240
超过参数721的领先模型

24
00:00:57,240 --> 00:00:58,659
比如Lava VDA

25
00:00:58,660 --> 00:00:59,500
还有

26
00:00:59,500 --> 00:01:02,700
中国团队推出Failu行动型浏览器

27
00:01:02,700 --> 00:01:04,620
或者智能体浏览器

28
00:01:04,620 --> 00:01:06,260
Agentech Browser

29
00:01:06,260 --> 00:01:07,820
能够根据用户的目标

30
00:01:07,820 --> 00:01:09,460
自主拆解任务

31
00:01:09,460 --> 00:01:12,340
支持跨网页的深度搜索和操作

32
00:01:12,340 --> 00:01:15,580
包括安全的访问需要登录的平台

33
00:01:15,580 --> 00:01:17,100
也就是说它可以在登录后

34
00:01:17,100 --> 00:01:18,379
访问私有数据

35
00:01:18,379 --> 00:01:22,300
比如像登录微博这种登录你的账号

36
00:01:22,300 --> 00:01:25,500
来更好完成端到端任务交付

37
00:01:25,500 --> 00:01:28,500
此外Failu支持影子空间

38
00:01:28,500 --> 00:01:29,939
Shadow Workspace
"""
    # Courier New
    # Impact
    add_subtitle(video_url, subtitle_content, False,
                 fontname="楷体", fontsize=16, fontcolor="&Hffffff",
                 fontbordercolor="&H000000", subtitle_bottom=16)
