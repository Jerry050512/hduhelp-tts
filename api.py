from typing import Literal, Union

# 添加用户语音（拼接）
def add_user_voice(
        audio_list: list[str] # 音频文件名列表
    ):
    '''拼接多个音频文件，生成一个新的音频文件。并清理原音频文件。'''
    return {
        "voice_filename": str
    }

# 语音合成
def tts(
        text: str,
        language: Literal["auto", "EN", "ES", "FR", "ZH", "JP", "KR"] = "auto",
        engine: Literal["melo", "chat"] = "melo",
        speaker_id: int | None = None,
        speed=1.0,
        refine_prompt: str | None = None
    ):
    '''利用指定的语音合成引擎，将文本转换为语音。'''
    return {
        "audio_filename": str
    }

# 语音置换
def voice_conversion(
        src_audio_filename: str,
        ref_voice_filename: str,
        speaker_key: str | None = None
    ):
    '''将源音频文件的语音特征转换为参考音频文件的语音特征。'''
    return {
        "converted_audio_filename": str
    }

# 语音识别（字幕生成）
def asr(
        audio_filename: str
    ):
    '''将音频文件转换为文本。'''
    return {
        "srt_filename": str
    }