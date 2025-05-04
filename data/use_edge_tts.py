import asyncio
import edge_tts
import requests


# 微软近期对中国区增加了 Sec-MS-GEC 和 Sec-MS-GEC-Version 参数校验，缺失或过期会导致 WSServerHandshakeError: 403 错误。
# 该限制仅针对中国 IP，国外用户不受影响。


async def text_to_speech(text, voice, output_file):
    # 动态获取 Sec 参数
    try:
        sec_data = requests.get("https://edgeapi.pyvideotrans.com/token.json").json()
    except:
        sec_data = {"Sec-MS-GEC": "", "Sec-MS-GEC-Version": ""}

    # 创建带参数的通信对象
    communicate = edge_tts.Communicate(
        text,
        voice,
        # proxy="http://127.0.0.1:7890",  # 若需代理
        custom_headers={
            "Sec-MS-GEC": sec_data.get("Sec-MS-GEC", ""),
            "Sec-MS-GEC-Version": sec_data.get("Sec-MS-GEC-Version", "")
        }
    )
    await communicate.save(output_file)
    # communicate = edge_tts.Communicate(text, voice)
    # await communicate.save(output_file)


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
    output_file = "D:\\sucai\\hello_world.mp3"

    # 运行异步函数
    asyncio.run(text_to_speech(text, voice, output_file))
    # print_voice_list()
