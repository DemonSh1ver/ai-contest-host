"""语音合成与播放（TTS）模块。

选型：``pyttsx3``（离线、免费，Windows 下走系统 SAPI5 语音引擎），
符合课内"离线、不联网"的交付边界。

职责：把主持词文本转为中文语音并播放。
"""

import pyttsx3


def init_engine():
    """初始化 TTS 引擎并做基础配置。

    - 优先选择系统里的中文语音（避免用英文语音朗读中文）。
    - 设置适合播报的语速与音量。
    """
    engine = pyttsx3.init()

    # 优先选中文本地化语音
    voices = engine.getProperty("voices")
    chinese_voice = None
    if isinstance(voices, list):
        for voice in voices:
            voice_id = str(getattr(voice, "id", ""))
            voice_name = str(getattr(voice, "name", ""))
            if "zh" in voice_id.lower() or "chinese" in voice_name.lower():
                chinese_voice = voice_id
                break

    if chinese_voice:
        engine.setProperty("voice", chinese_voice)
        print("[TTS] 已选用中文语音")
    else:
        print("[TTS] 警告：未检测到中文语音，可能以英文语音朗读中文，建议安装中文语音包")

    # 语速稍慢，适合播报
    engine.setProperty("rate", 170)
    # 音量 0.0 ~ 1.0
    engine.setProperty("volume", 0.9)

    return engine


def speak(engine, text):
    """将文本转为语音并播放。"""
    engine.say(text)
    engine.runAndWait()
