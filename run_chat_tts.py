import sys
import torch
from Chat.core import Chat
from Chat.norm import Normalizer
import os
import numpy as np
import scipy.io.wavfile as wav

class ChatTTS:
    def __init__(self, config_path, model_path, device=None):
        """
        Args:
            config_path (str): 配置文件路径。
            model_path (str): 模型文件路径。
            device (str): 设备类型，'cuda' 或 'cpu'，默认为自动选择。
        """
        self.config_path = config_path
        self.model_path = model_path
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.chat = Chat()
        self.normalizer = Normalizer(config_path +"/homophones_map.json")

        self.output_dir = "assets/tts_audio"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load(self):
        success = self.chat.load(source="local", custom_path=self.model_path)
        if not success:
            raise RuntimeError("Failed to load the model.")
        print("Model loaded successfully.")
    
    def infer(self, text, lang="zh", speaker_id=None, speed=1.0, refine_prompt=None, audio_name="output_audio.wav"):
        """
        Args:
            text (str): 输入的文本内容。
            lang (str): 语言选择，默认中文 ("zh")。
            speaker_id (str): 可选，指定使用的声音样本（如果有）。
            speed (float): 语速，默认为 1.0。
            refine_prompt (str): 情感或语调标记（例如 `[laugh]`）。
            audio_name (str): 输出的音频文件名，默认为 "output_audio.wav"。

        Returns:
            audio_data (np.ndarray): 生成的语音数据。
        """
        norm_text = self.normalizer(text)
        
        if refine_prompt:
            norm_text += " " + refine_prompt

        audio_data = self.chat.infer(
            text=norm_text, 
            lang=lang, 
            params_infer_code={"spk_smp": speaker_id} 
        )

        audio_path = os.path.join(self.output_dir, audio_name)

        wav.write(audio_path, 44100, audio_data.astype(np.int16))

        print(f"Audio saved to {audio_path}")
        
        return audio_data
    
current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(current_dir, 'Chat'))

from chat_tts_model import ChatTTS  

if __name__ == "__main__":

    chat_tts = ChatTTS(config_path="C:\chat\Chat\config", model_path="C:\chat\Chat\model")
    
    chat_tts.load()
    
    text = "你好，欢迎使用 ChatTTS！"
    audio = chat_tts.infer(text, lang="zh", speaker_id="speaker1", speed=1.0, refine_prompt="[laugh]", audio_name="example_output.wav")  # 生成语音并保存为 "example_output.wav"
