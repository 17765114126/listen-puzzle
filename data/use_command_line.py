import subprocess


# whisper E:\微电影案例.mp4 --task transcribe --language Chinese --device cuda --model medium -f srt  --model_dir C:\Users\1\AppData\Local\Buzz\Buzz\Cache\models\whisper

# Whipser 推出了 tiny、base、small、medium、large 5 个档次的模型。转录效果依次增加，但相应花费的时间也会增加。
# Whisper 使用了 Python 开发，安装后，在文件所在目录打开终端，运行 whisper audio.mp3 即可进行转录。
# 想要自定义设置的话，则可以在后面追加命令参数，具体包括：

# whisper audio.mp3 --命令参数

# --task :指定转录方式(默认转录模式)
# transcribe 转录模式，
# translate 则为翻译模式，目前只支持英文。

# --model :指定使用模型(默认:small)
# Whisper 还有英文专用模型，就是在名称后加上 .en，这样速度更快。

# --language :指定转录语言(支持语言，使用--help查询)
# 若不指定默认会截取 30 秒来判断语种，但最好指定为某种语言，比如指定中文是 --language Chinese。

# --device :指定硬件加速(默认：cpu)
# --device cuda 则为显卡，cpu 就是 CPU， mps 为苹果 M1 芯片。

# --help:帮助
# whisper --help

# --model_dir : 模型地址
# 保存模型文档的路径;默认使用 ~/.cache/whisper（默认：None）

# --output_dir, -o  输出文件目录
# 目录来保存输出(默认:.)

# --output_format, -f :输出文件的格式;如果未指定，则将生成所有可用格式(默认:all)
# txt：基本的文本文件格式
# vtt：Web视频文本轨道，是一种用于为视频文件提供字幕、描述和其他元数据的文件格式
# srt：SubRip字幕，常见的视频字幕文件格式。
# tsv：制表符分隔值，用于存储结构化数据的文本文件格式。
# json：JavaScript对象表示法，一种轻量级的数据交换格式。

# --verbose VERBOSE :控制台是否打印出进度和调试消息(默认:True)

#  --fp16 ：是否在 fp16 中执行推理;默认为 True(默认:True)

def sub_transcribe():
    # 定义命令行及其参数
    command = "whisper"
    arguments = [
        "E:\\微电影案例.mp4",
        "--task", "transcribe",
        "--language", "Chinese",
        "--device", "cuda",
        "--model", "medium",
        "-f", "srt",
        "--model_dir", "C:\\Users\\1\\AppData\\Local\\Buzz\\Buzz\\Cache\\models\\whisper"
    ]

    # 使用subprocess.run()执行命令
    result = subprocess.run([command] + arguments)

    # 检查命令是否成功执行
    if result.returncode == 0:
        print("命令执行成功")
    else:
        print("命令执行失败，错误码：", result.returncode)
