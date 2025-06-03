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
    def __init__(self, output_srt_dir, model="turbo"): # output_srt_dir is now a required positional argument
        self.model = whisper.load_model(model)
        self.output_srt_dir = Path(output_srt_dir) # Assign parameter and ensure it's a Path object

        # The instruction is to keep this for now, but using the new variable name.
        # If the server manages the creation of the full output path's directory, this might be redundant.
        os.makedirs(self.output_srt_dir, exist_ok=True)
    
    def transcribe(self, audio_file, output_srt_filepath: str | Path | None = None, language="auto"): # output_srt changed to output_srt_filepath
        if language == "auto":
            result = self.model.transcribe(audio_file)
        else:
            result = self.model.transcribe(audio_file, language=language)

        # If output_srt_filepath is provided, save SRT to this exact path
        if output_srt_filepath is not None:
            # Ensure output_srt_filepath is a Path object if it's a string
            srt_path = Path(output_srt_filepath) if isinstance(output_srt_filepath, str) else output_srt_filepath
            # The directory for srt_path should be created by the caller if it's a full path.
            # If only a filename was intended to be passed, self.output_srt_dir would be prepended.
            # Based on "full file path including filename and extension", we use it directly.
            list_to_srt(result["segments"], srt_filename=srt_path)
        return result["text"]

if __name__ == '__main__':
    # Example usage reflecting changes: output_srt_dir is now mandatory.
    # The output_srt parameter in transcribe is now output_srt_filepath (a full path).
    temp_output_dir = Path("./temp_srt_output") # Example output directory for the test
    asr = WhisperASR(output_srt_dir=temp_output_dir, model="tiny")

    # Example: Save SRT to a specific file path
    example_srt_filepath = temp_output_dir / "output_v2_zh.srt"
    asr.transcribe("assets/output/convert_audio/output_v2_zh.wav", language="zh", output_srt_filepath=example_srt_filepath)
    print(f"SRT 字幕文件 '{example_srt_filepath}' 已生成。")

    # Example: Transcribe without saving SRT
    # text_only = asr.transcribe("assets/output/convert_audio/output_v2_zh.wav", language="zh", output_srt_filepath=None)
    # print(f"Transcription result (no SRT saved): {text_only}")