import asyncio
import edge_tts


async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)


# 获取所有可用的声音
#  get role by edge tts
async def get_edge_voicelist():
    # 调用 list_voices 方法并等待结果
    voices = await edge_tts.list_voices()
    return voices


def print_voice_list():
    # 运行异步函数并获取结果
    voices = asyncio.run(get_edge_voicelist())
    for voice in voices:
        print(voice)


if __name__ == '__main__':
    # 多种语言和风格的声音，
    # 访问 Azure 文档：
    # https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/language-support?spm=5176.28103460.0.0.1c235d27Ri9whH&tabs=tts#neural-voices
    # 示例：将文本 "Hello, world!" 转换成英语女声，并保存为 hello_world.mp3
    text = "Hello, world!"
    voice = "en-GB-SoniaNeural"  # 使用英国英语的 Sonia 声音
    output_file = "hello_world.mp3"

    # 运行异步函数
    # asyncio.run(text_to_speech(text, voice, output_file))
    print_voice_list()
