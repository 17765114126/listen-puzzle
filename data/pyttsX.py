import pyttsx3


def speak(audioString):
    # 初始化:
    engine = pyttsx3.init()

    # 设置中文
    # engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-CN_HUIHUI_11.0")

    # 添加语音文本：
    engine.say(audioString)

    # 音量调节
    # vol = engine.getProperty('volume')
    # engine.setProperty('vol', vol + 0.5)

    # 对于发音，频率，变声则为 vioce，rate，vioces，是不是很好理解了？当然，如果你想让它循环播放，只需加一个事件驱动循环即可：\
    # engine.startLoop()

    # 运行：
    engine.runAndWait()


if __name__ == '__main__':
    speak("你好")
