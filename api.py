from typing import Literal, Union
from pathlib import Path
from os.path import splitext, basename
import random

from utils.audio import concatenate_audio_files
from utils.hash_file import generate_unique_filename_hash, generate_text_hash_filename
from utils.language_detect import detect_language

from melo import Melo
from tone_convert import ToneConvert
from whisper_asr import WhisperASR

print("Start loading models...")
melo_api = Melo()
tc_api = ToneConvert()
whisper_api = WhisperASR()

AUDIO_INPUT_DIR = Path("assets/input/audio")

# 添加用户语音（拼接）
def add_user_voice(
        audio_list: list[str] # 音频文件名列表
    ):
    '''拼接多个音频文件，生成一个新的音频文件。并清理原音频文件。'''

    
    audio_list = [AUDIO_INPUT_DIR / audio for audio in audio_list]
    output_filename = generate_unique_filename_hash(audio_list, ".mp3")
    successful = concatenate_audio_files(audio_list, output_filename, remove_inputs=True)
    
    tc_api.get_se(ref_audio_file=AUDIO_INPUT_DIR / output_filename)
    tc_api.save_ref_se()
    
    if successful:
        return {
            "audio_filename": output_filename, 
            "error": ""
        }
    else:
        return {
            "audio_filename": None,
            "error": "Failed to concatenate audio files."
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

    if language == "auto":
        language = detect_language(text)
        if language == "Unknown":
            return {
                "audio_filename": None,
                "error": "Language detection failed. Please specify the language manully."
            }
    
    audio_filename = generate_text_hash_filename(f"{text}\n{random.random()}", ".mp3")
        
    if engine == "melo":
        if melo_api.language != language:
            melo_api.load(language=language)
        
        melo_api.infer(text, speaker_id=speaker_id, speed=speed, refine_prompt=refine_prompt, audio_name=audio_filename)
    
    if engine == "chat":
        return {
            "audio_filename": None,
            "error": "ChatTTS engine is not available."
        }
        
    return {
        "audio_filename": audio_filename,
        "error": ""
    }

# 语音置换
def voice_conversion(
        src_audio_file: str,
        ref_voice_filename: str,
        speaker_key: str | None = None
    ):
    '''将源音频文件的语音特征转换为参考音频文件的语音特征。'''
    ref_speaker_key = splitext(basename(ref_voice_filename))[0]
    tc_api.get_se(ref_speaker_key=ref_speaker_key, speaker_key=speaker_key)
    tc_api.convert_tone_color(src_audio_file)
    return {
        "converted_audio_filename": basename(src_audio_file),
        "error": ""
    }

# 语音识别（字幕生成）
def asr(
        audio_filename: str, 
        language: str = "auto"
    ):
    '''将音频文件转换为文本。'''

    srt_filename = generate_unique_filename_hash([audio_filename], ".srt")
    whisper_api.transcribe(AUDIO_INPUT_DIR / audio_filename, language=language, output_srt=srt_filename)
    return {
        "srt_filename": srt_filename,
        "error": ""
    }

