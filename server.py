import grpc
from concurrent import futures
import os
import uuid # Added
from pathlib import Path # Added
import shutil # Added

from proto import audio_pb2_grpc, audio_pb2
from service import oss
import ulid # This was used in AddUserVoice, keeping it.
import api # Added


# Load OSS credentials and configurations from environment variables
OSS_ACCESS_KEY_ID = os.getenv("OSS_ACCESS_KEY_ID")
OSS_ACCESS_KEY_SECRET = os.getenv("OSS_ACCESS_KEY_SECRET")
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
OSS_BUCKET_NAME = os.getenv("OSS_BUCKET_NAME", "hdu-tts-test")

if not OSS_ACCESS_KEY_ID or not OSS_ACCESS_KEY_SECRET:
    raise ValueError("OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET must be set in environment variables")

# Define and create temporary directory
TMP_AUDIO_DIR = os.getenv("TMP_AUDIO_DIR", "/tmp/audio_processing_data")
if not os.path.exists(TMP_AUDIO_DIR):
    os.makedirs(TMP_AUDIO_DIR)
    print(f"Created temporary directory: {TMP_AUDIO_DIR}")


class AudioService(audio_pb2_grpc.AudioServiceServicer):
    def __init__(self, oss_client):
        self.oss_client = oss_client

    def AddUserVoice(self, request, context):
        request_id = str(uuid.uuid4())
        base_temp_dir = Path(os.getenv('TMP_AUDIO_DIR', '/tmp/audio_processing_data'))
        request_temp_dir = base_temp_dir / request_id

        local_input_audio_filepaths = []

        try:
            os.makedirs(request_temp_dir, exist_ok=True)
            local_input_audio_dir = request_temp_dir / "inputs"
            os.makedirs(local_input_audio_dir, exist_ok=True)

            if not request.audio_list:
                context.set_details("No audio files provided in the request.")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return audio_pb2.AddUserVoiceResponse()

            for oss_audio_path in request.audio_list:
                if not oss_audio_path.strip(): # Skip empty paths
                    continue
                local_filepath = local_input_audio_dir / Path(oss_audio_path).name
                try:
                    print(f"Downloading input audio {oss_audio_path} to {local_filepath}")
                    self.oss_client.download_file(oss_audio_path, str(local_filepath))
                    local_input_audio_filepaths.append(str(local_filepath))
                except Exception as e:
                    error_message = f"Failed to download input audio '{oss_audio_path}' from OSS: {str(e)}"
                    print(error_message)
                    context.set_details(error_message)
                    context.set_code(grpc.StatusCode.NOT_FOUND) # Or INTERNAL depending on OSS client behavior
                    return audio_pb2.AddUserVoiceResponse()

            if not local_input_audio_filepaths:
                context.set_details("No valid audio files could be processed from the request list.")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return audio_pb2.AddUserVoiceResponse()

            # Prepare output paths
            unique_output_stem = str(uuid.uuid4())
            # Assuming api.add_user_voice output concatenated audio is .wav based on other methods
            local_output_concatenated_filepath = request_temp_dir / f"{unique_output_stem}_voice.wav"
            local_output_speaker_embedding_filepath = request_temp_dir / f"{unique_output_stem}_embedding.pth"

            # Call api.add_user_voice
            print(f"Calling api.add_user_voice for {len(local_input_audio_filepaths)} files.")
            result = api.add_user_voice(
                input_audio_filepaths=local_input_audio_filepaths,
                output_concatenated_filepath=str(local_output_concatenated_filepath),
                output_speaker_embedding_filepath=str(local_output_speaker_embedding_filepath),
                temp_processing_dir=str(request_temp_dir)
            )

            if result.get("error"):
                error_message = f"api.add_user_voice failed: {result['error']}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.AddUserVoiceResponse()

            # Upload concatenated audio and speaker embedding to OSS
            oss_concatenated_audio_path = f"user_voices/audio/{Path(result['audio_filename']).name}"
            oss_speaker_embedding_path = f"user_voices/speaker_embeddings/{Path(result['speaker_embedding_filename']).name}"

            try:
                print(f"Uploading concatenated audio {result['audio_filename']} to {oss_concatenated_audio_path}")
                self.oss_client.upload_file(result['audio_filename'], oss_concatenated_audio_path)
            except Exception as e:
                error_message = f"Failed to upload concatenated audio to OSS: {str(e)}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                # Potentially delete embedding if audio upload fails? For now, just error out.
                return audio_pb2.AddUserVoiceResponse()

            try:
                print(f"Uploading speaker embedding {result['speaker_embedding_filename']} to {oss_speaker_embedding_path}")
                self.oss_client.upload_file(result['speaker_embedding_filename'], oss_speaker_embedding_path)
            except Exception as e:
                error_message = f"Failed to upload speaker embedding to OSS: {str(e)}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                # Potentially delete concatenated audio if embedding upload fails? For now, just error out.
                return audio_pb2.AddUserVoiceResponse()

            # The problem statement implies the .pth file is also important, but the response only has one field.
            # For now, returning the audio path as requested.
            # A more robust solution might return both paths or a common identifier.
            return audio_pb2.AddUserVoiceResponse(voice_filename=oss_concatenated_audio_path)

        except Exception as e:
            error_message = f"Unexpected error in AddUserVoice method: {str(e)}"
            print(error_message)
            context.set_details(error_message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return audio_pb2.AddUserVoiceResponse()
        finally:
            if os.path.exists(request_temp_dir):
                print(f"Cleaning up temporary directory: {request_temp_dir}")
                shutil.rmtree(request_temp_dir)

    def TTS(self, request, context):
        request_id = str(uuid.uuid4())
        base_temp_dir = Path(os.getenv('TMP_AUDIO_DIR', '/tmp/audio_processing_data'))
        request_temp_dir = base_temp_dir / request_id

        try:
            os.makedirs(request_temp_dir, exist_ok=True)
            local_output_audio_filepath = request_temp_dir / f"{request_id}_tts_output.wav"

            # Handle optional gRPC fields
            speaker_id_to_pass = request.speaker_id if request.HasField("speaker_id") else None
            refine_prompt_to_pass = request.refine_prompt if request.HasField("refine_prompt") else None

            # Assuming request.text_filename IS the actual text content as per instructions
            # Assuming request.language, request.engine, request.speed are always provided (not optional in proto)
            result = api.tts(
                text=request.text_filename,
                output_audio_filepath=str(local_output_audio_filepath),
                language=request.language,
                engine=request.engine,
                speaker_id=speaker_id_to_pass,
                speed=request.speed,
                refine_prompt=refine_prompt_to_pass
            )

            if result.get("error"):
                error_message = f"api.tts failed: {result['error']}"
                print(error_message) # Log error
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.TTSResponse()

            # Upload to OSS
            oss_output_path = f"tts_output/{local_output_audio_filepath.name}"
            try:
                self.oss_client.upload_file(str(local_output_audio_filepath), oss_output_path)
            except Exception as e:
                error_message = f"Failed to upload TTS output to OSS: {str(e)}"
                print(error_message) # Log error
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.TTSResponse()

            return audio_pb2.TTSResponse(audio_filename=oss_output_path)

        except Exception as e:
            # Catch any other unexpected errors during the process
            error_message = f"Unexpected error in TTS method: {str(e)}"
            print(error_message) # Log error
            context.set_details(error_message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return audio_pb2.TTSResponse()
        finally:
            if os.path.exists(request_temp_dir):
                shutil.rmtree(request_temp_dir)

    def VoiceConversion(self, request, context):
        request_id = str(uuid.uuid4())
        base_temp_dir = Path(os.getenv('TMP_AUDIO_DIR', '/tmp/audio_processing_data'))
        request_temp_dir = base_temp_dir / request_id

        try:
            os.makedirs(request_temp_dir, exist_ok=True)

            # Define local filepaths
            local_src_audio_filepath = request_temp_dir / Path(request.src_audio_filename).name
            local_ref_voice_filepath = request_temp_dir / Path(request.ref_voice_filename).name
            local_output_converted_audio_filepath = request_temp_dir / f"converted_{Path(request.src_audio_filename).name}"

            # Download source audio from OSS
            try:
                print(f"Downloading source audio {request.src_audio_filename} to {local_src_audio_filepath}")
                self.oss_client.download_file(request.src_audio_filename, str(local_src_audio_filepath))
            except Exception as e:
                error_message = f"Failed to download source audio '{request.src_audio_filename}' from OSS: {str(e)}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return audio_pb2.VoiceConversionResponse()

            # Download reference voice embedding (.pth file) from OSS
            try:
                print(f"Downloading reference voice embedding {request.ref_voice_filename} to {local_ref_voice_filepath}")
                self.oss_client.download_file(request.ref_voice_filename, str(local_ref_voice_filepath))
            except Exception as e:
                error_message = f"Failed to download reference voice embedding '{request.ref_voice_filename}' from OSS: {str(e)}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return audio_pb2.VoiceConversionResponse()

            # Call api.voice_conversion
            # speaker_key is optional in api.voice_conversion and not available from request, so pass None.
            print(f"Calling api.voice_conversion for {local_src_audio_filepath} with reference {local_ref_voice_filepath}")
            result = api.voice_conversion(
                src_audio_filepath=str(local_src_audio_filepath),
                ref_voice_embedding_filepath=str(local_ref_voice_filepath),
                output_converted_audio_filepath=str(local_output_converted_audio_filepath),
                temp_processing_dir=str(request_temp_dir), # api.voice_conversion uses this for its own temp needs if any
                speaker_key=None
            )

            if result.get("error"):
                error_message = f"api.voice_conversion failed: {result['error']}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.VoiceConversionResponse()

            # Upload converted audio to OSS
            oss_converted_audio_output_path = f"voice_conversion_output/{local_output_converted_audio_filepath.name}"
            try:
                print(f"Uploading {local_output_converted_audio_filepath} to {oss_converted_audio_output_path}")
                self.oss_client.upload_file(str(local_output_converted_audio_filepath), oss_converted_audio_output_path)
            except Exception as e:
                error_message = f"Failed to upload converted audio to OSS: {str(e)}"
                print(error_message)
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.VoiceConversionResponse()

            return audio_pb2.VoiceConversionResponse(converted_audio_filename=oss_converted_audio_output_path)

        except Exception as e:
            error_message = f"Unexpected error in VoiceConversion method: {str(e)}"
            print(error_message)
            context.set_details(error_message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return audio_pb2.VoiceConversionResponse()
        finally:
            if os.path.exists(request_temp_dir):
                print(f"Cleaning up temporary directory: {request_temp_dir}")
                shutil.rmtree(request_temp_dir)

    def ASR(self, request, context):
        request_id = str(uuid.uuid4())
        base_temp_dir = Path(os.getenv('TMP_AUDIO_DIR', '/tmp/audio_processing_data'))
        request_temp_dir = base_temp_dir / request_id
        local_input_audio_filepath = None # Define for visibility in finally

        try:
            os.makedirs(request_temp_dir, exist_ok=True)

            # Download audio file from OSS
            # Assuming request.audio_filename is the full path in OSS
            local_input_audio_filepath = request_temp_dir / Path(request.audio_filename).name
            try:
                print(f"Downloading {request.audio_filename} to {local_input_audio_filepath}")
                self.oss_client.download_file(request.audio_filename, str(local_input_audio_filepath))
            except Exception as e:
                error_message = f"Failed to download source audio from OSS '{request.audio_filename}': {str(e)}"
                print(error_message) # Log error
                context.set_details(error_message)
                # Determine appropriate status code, e.g. if it's a known "not found" from OSS client
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return audio_pb2.ASRResponse()

            # Prepare output SRT path
            local_output_srt_filepath = request_temp_dir / f"{Path(request.audio_filename).stem}.srt"

            # Call api.asr
            # Assuming request has a 'language' field. If not, default to "auto" or adjust as needed.
            asr_language = request.language if hasattr(request, 'language') and request.language else "auto"
            print(f"Calling api.asr for {local_input_audio_filepath} with language {asr_language}")
            result = api.asr(
                input_audio_filepath=str(local_input_audio_filepath),
                output_srt_filepath=str(local_output_srt_filepath),
                language=asr_language
            )

            if result.get("error"):
                error_message = f"api.asr failed: {result['error']}"
                print(error_message) # Log error
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.ASRResponse()

            # Upload SRT file to OSS
            oss_srt_output_path = f"asr_output/{local_output_srt_filepath.name}"
            try:
                print(f"Uploading {local_output_srt_filepath} to {oss_srt_output_path}")
                self.oss_client.upload_file(str(local_output_srt_filepath), oss_srt_output_path)
            except Exception as e:
                error_message = f"Failed to upload SRT file to OSS: {str(e)}"
                print(error_message) # Log error
                context.set_details(error_message)
                context.set_code(grpc.StatusCode.INTERNAL)
                return audio_pb2.ASRResponse()

            return audio_pb2.ASRResponse(srt_filename=oss_srt_output_path)

        except Exception as e:
            # Catch any other unexpected errors during the process
            error_message = f"Unexpected error in ASR method: {str(e)}"
            print(error_message) # Log error
            context.set_details(error_message)
            context.set_code(grpc.StatusCode.INTERNAL)
            return audio_pb2.ASRResponse()
        finally:
            if os.path.exists(request_temp_dir):
                print(f"Cleaning up temporary directory: {request_temp_dir}")
                shutil.rmtree(request_temp_dir)

def serve():
    # 创建 OSS 客户端
    oss_client = oss.OSSClient(
        access_key_id=OSS_ACCESS_KEY_ID,
        access_key_secret=OSS_ACCESS_KEY_SECRET,
        endpoint=OSS_ENDPOINT,
        bucket_name=OSS_BUCKET_NAME,
    )

    # 创建服务器
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_pb2_grpc.add_AudioServiceServicer_to_server(AudioService(oss_client), server)
    server.add_insecure_port('[::]:50051')
    print("Starting server on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()