from typing import Literal, Union, List
from pathlib import Path

from utils.audio import concatenate_audio_files
from utils.language_detect import detect_language

from melo import Melo
from tone_convert import ToneConvert
from whisper_asr import WhisperASR

# Global initializations and AUDIO_INPUT_DIR removed

def add_user_voice(
        input_audio_filepaths: List[str],
        output_concatenated_filepath: str,
        output_speaker_embedding_filepath: str,
        temp_processing_dir: str
    ):
    '''拼接多个音频文件，生成一个新的音频文件。并提取其声音特征保存。'''
    try:
        output_concat_path = Path(output_concatenated_filepath)
        output_embed_path = Path(output_speaker_embedding_filepath)
        temp_proc_dir = Path(temp_processing_dir)

        # Ensure parent directories exist for outputs and temporary processing
        output_concat_path.parent.mkdir(parents=True, exist_ok=True)
        output_embed_path.parent.mkdir(parents=True, exist_ok=True)
        temp_proc_dir.mkdir(parents=True, exist_ok=True)

        tc_api = ToneConvert(
            custom_speakers_ses_dir=str(output_embed_path.parent),
            output_dir=str(output_concat_path.parent)
        )

        input_paths = [Path(p) for p in input_audio_filepaths]

        successful_concat = concatenate_audio_files(
            input_filepaths=input_paths,
            output_filename=output_concat_path,
            remove_inputs=True # As per original logic
        )

        if not successful_concat:
            return {
                "audio_filename": None,
                "speaker_embedding_filename": None,
                "error": "Failed to concatenate audio files."
            }

        # Extract speaker embedding from the concatenated audio
        tc_api.get_se(
            intermediate_dir=str(temp_proc_dir),
            ref_audio_file=str(output_concat_path)
        )

        # Ensure target_se_ckpt is set to the desired filename for the embedding
        tc_api.target_se_ckpt = output_embed_path.name
        tc_api.save_ref_se() # Saves to the path constructed from custom_speakers_ses_dir and target_se_ckpt

        return {
            "audio_filename": str(output_concat_path),
            "speaker_embedding_filename": str(output_embed_path),
            "error": ""
        }
    except Exception as e:
        return {
            "audio_filename": None,
            "speaker_embedding_filename": None,
            "error": f"An error occurred in add_user_voice: {str(e)}"
        }

def tts(
        text: str,
        output_audio_filepath: str,
        language: Literal["auto", "EN", "ES", "FR", "ZH", "JP", "KR"] = "auto",
        engine: Literal["melo", "chat"] = "melo",
        speaker_id: int | None = None,
        speed=1.0,
        refine_prompt: str | None = None
    ):
    '''利用指定的语音合成引擎，将文本转换为语音。'''
    try:
        output_audio_path = Path(output_audio_filepath)
        output_audio_path.parent.mkdir(parents=True, exist_ok=True)

        if language == "auto":
            detected_lang = detect_language(text)
            if detected_lang == "Unknown":
                return {
                    "audio_filename": None,
                    "error": "Language detection failed. Please specify the language manually."
                }
            language = detected_lang

        if engine == "melo":
            # Melo's output_dir is used if output_path in infer is relative,
            # but we provide an absolute path. It's still good practice to set it.
            melo_api = Melo(output_dir=str(output_audio_path.parent))
            melo_api.load(language=language)

            melo_api.infer(
                text,
                output_path=output_audio_path, # Pass Path object directly
                speaker_id=speaker_id,
                speed=speed,
                refine_prompt=refine_prompt # Melo will warn if not None
            )
        elif engine == "chat":
            return {
                "audio_filename": None,
                "error": "ChatTTS engine is not available."
            }
        else:
            return {
                "audio_filename": None,
                "error": f"Unsupported TTS engine: {engine}"
            }

        return {
            "audio_filename": str(output_audio_path),
            "error": ""
        }
    except Exception as e:
        return {
            "audio_filename": None,
            "error": f"An error occurred in tts: {str(e)}"
        }

def voice_conversion(
        src_audio_filepath: str,
        ref_voice_embedding_filepath: str,
        output_converted_audio_filepath: str,
        temp_processing_dir: str,
        speaker_key: str | None = None # For base_speakers_ses in ToneConvert
    ):
    '''将源音频文件的语音特征转换为参考音频文件的语音特征。'''
    try:
        src_audio_path = Path(src_audio_filepath)
        ref_embed_path = Path(ref_voice_embedding_filepath)
        output_converted_path = Path(output_converted_audio_filepath)
        temp_proc_dir = Path(temp_processing_dir)

        # Ensure output and temp directories exist
        output_converted_path.parent.mkdir(parents=True, exist_ok=True)
        temp_proc_dir.mkdir(parents=True, exist_ok=True)
        # Assumption: ref_voice_embedding_filepath and its parent directory already exist.

        tc_api = ToneConvert(
            custom_speakers_ses_dir=str(ref_embed_path.parent),
            output_dir=str(output_converted_path.parent)
        )

        # Get speaker embeddings
        tc_api.get_se(
            intermediate_dir=str(temp_proc_dir),
            ref_speaker_key=ref_embed_path.stem, # Get filename without .pth
            src_audio_file=str(src_audio_path), # For source SE if speaker_key is None
            speaker_key=speaker_key # For target SE from base_speakers_ses if provided
        )

        converted_path_str = tc_api.convert_tone_color(
            src_audio_file=str(src_audio_path),
            output_filepath=output_converted_path # Pass Path object
        )

        return {
            "converted_audio_filename": converted_path_str,
            "error": ""
        }
    except Exception as e:
        return {
            "converted_audio_filename": None,
            "error": f"An error occurred in voice_conversion: {str(e)}"
        }

def asr(
        input_audio_filepath: str,
        output_srt_filepath: str | None, # Can be None if SRT file is not needed
        language: str = "auto"
    ):
    '''将音频文件转换为文本。'''
    try:
        input_audio_path = Path(input_audio_filepath)
        output_srt_path_obj = Path(output_srt_filepath) if output_srt_filepath else None

        # WhisperASR constructor needs an output_srt_dir.
        # If output_srt_filepath is provided, use its parent. Otherwise, a default temporary dir.
        # This directory is for WhisperASR's internal use if it were to construct paths itself,
        # but we pass the full output_srt_filepath to transcribe.
        whisper_init_output_dir = "/tmp/asr_default_output_dir" # A sensible default
        if output_srt_path_obj:
            output_srt_path_obj.parent.mkdir(parents=True, exist_ok=True)
            whisper_init_output_dir = str(output_srt_path_obj.parent)

        whisper_api = WhisperASR(output_srt_dir=whisper_init_output_dir)

        transcribed_text = whisper_api.transcribe(
            audio_file=str(input_audio_path),
            output_srt_filepath=output_srt_path_obj, # Pass Path object or None
            language=language
        )

        # Return the string representation of the path, or None
        returned_srt_filepath_str = str(output_srt_path_obj) if output_srt_path_obj else None

        return {
            "text": transcribed_text,
            "srt_filename": returned_srt_filepath_str,
            "error": ""
        }
    except Exception as e:
        return {
            "text": None,
            "srt_filename": None,
            "error": f"An error occurred in asr: {str(e)}"
        }
