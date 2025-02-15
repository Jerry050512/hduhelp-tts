import whisper
import os
from pathlib import Path
from utils.lst2srt import list_to_srt

# model = whisper.load_model("tiny")
# result = model.transcribe("assets/output/convert_audio/output_v2_zh.wav", language="en")
# print(result["text"])
# print(result.keys())
# print(result["segments"])
# print(result["language"])

class WhisperASR:
    def __init__(self, model="turbo"):
        self.model = whisper.load_model(model)
        self.output_srt_path = Path("assets/output/srt")

        os.makedirs(self.output_srt_path, exist_ok=True)
    
    def transcribe(self, audio_file, language="auto", output_srt: str | None = None):
        if language == "auto":
            result = self.model.transcribe(audio_file)
        else:
            result = self.model.transcribe(audio_file, language=language)
        if output_srt is not None:
            list_to_srt(result["segments"], srt_filename=self.output_srt_path / output_srt)
        return result["text"]

if __name__ == '__main__':
    asr = WhisperASR(model="tiny")
    asr.transcribe("assets/output/convert_audio/output_v2_zh.wav", language="zh", output_srt="output.srt")
    print("SRT 字幕文件 'output.srt' 已生成。")