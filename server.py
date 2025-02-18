import grpc
from concurrent import futures

from proto import audio_pb2_grpc, audio_pb2
from service import oss
import ulid


class AudioService(audio_pb2_grpc.AudioServiceServicer):
    def __init__(self, oss_client):
        self.oss_client = oss_client

    def AddUserVoice(self, request, context):
        # 处理用户语音添加请求
        # 读取许多声音文件，处理成一个，可能需要统一格式
        for file_name in request.audio_list:
            print(f"Processing {file_name}")
            # self.oss_client.download_file(f"origin/{file_name}", f"./file/{file_name}")

        # 处理上传的音频 生成新的音频文件

        # 删除旧文件
        # for file_name in request.audio_list:
        #     self.oss_client.delete_file(f"origin/{file_name}")

        # 生成新的文件名
        newName = str(ulid.ULID()) # 保证唯一
        print(newName)
        # 上传处理后的声音文件
        # 可能需要加上 格式 后缀
        # self.oss_client.upload_file(f"./file/{newName}", f"model/{newName}")
        # 这里添加实际的音频处理逻辑
        return audio_pb2.AddUserVoiceResponse(voice_filename=newName)

    def TTS(self, request, context):
        # 处理文本转语音请求
        audio_file = f"tts_output_{request.text_filename}.wav"
        # 这里添加实际的TTS转换逻辑
        return audio_pb2.TTSResponse(audio_filename=audio_file)

    def VoiceConversion(self, request, context):
        # 处理声音转换请求
        output_file = f"converted_{request.src_audio_filename}"
        # 这里添加实际的声音转换逻辑
        return audio_pb2.VoiceConversionResponse(converted_audio_filename=output_file)

    def ASR(self, request, context):
        # 处理语音识别请求
        srt_file = f"{request.audio_filename}.srt"
        # 这里添加实际的语音识别逻辑
        return audio_pb2.ASRResponse(srt_filename=srt_file)

def serve():
    # 创建 OSS 客户端
    oss_client = oss.OSSClient(
        access_key_id="accessKeyId",
        access_key_secret="accessKeySecret",
        endpoint="oss-cn-hangzhou.aliyuncs.com",
        bucket_name="hdu-tts-test",
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