from MeloTTS.melo.api import TTS
from pathlib import Path
import os
import torch
from utils.download_all_tts_model import download_all_melo_model

class Melo:
    def __init__(self):
        self.model: TTS | None = None
        self.speaker_ids: dict | None = None
        self.sample_rate = 44100
        self.output_dir = Path("assets/output/tts_audio")
        self.language: str | None = None

    def load(self, language='EN', device='auto'):
        self.model = TTS(language=language, device=device)
        self.speaker_ids = self.model.hps.data.spk2id
        self.sample_rate = self.model.hps.data.sampling_rate
        self.language = language
    
    def unload(self):
        if self.model is not None:
            if torch.cuda.is_available(): # check if cuda is available
                self.model.model.cpu() # move model to cpu if it is on cuda.
                torch.cuda.empty_cache() # clear cache.
            del self.model
            self.model = None
            self.speaker_ids = None # clear speaker ids
            print("Model unloaded.")
        else:
            print("Model was not loaded, nothing to unload.")
    
    def show_speakers(self):
        if self.speaker_ids is None:
            print("No speakers available. Load model first.")
        else:
            print("Available speakers:")
            for speaker, speaker_id in self.speaker_ids.items():
                print(f"Speaker: {speaker}, ID: {speaker_id}")

    def infer(
            self, 
            text: str, 
            speaker_id: int | None = None, 
            speed=1.0, 
            refine_prompt: str | None = None, 
            audio_name: str | None = None
        ):
        '''
        Generate audio from text using MeloTTS.
                
        Args:
            text (str): The input text to be converted into speech.
            speaker_id (int | None, optional): The ID of the speaker to use. If None, the default speaker will be selected.
            speed (float, optional): The speed of speech synthesis. Should be between 0.3 and 3.0. Defaults to 1.0.
            refine_prompt (str | None, optional): Not supported in MeloTTS. If provided, a UserWarning will be raised.
            audio_name (str | None, optional): The name of the output audio file (without extension). If None, the output will not be saved to a file.
        
        Returns:
            None: The synthesized speech is directly processed by the model.
        
        Raises:
            UserWarning: If the model is not loaded before inference.
            UserWarning: If `refine_prompt` is provided, as it is not supported.
            AssertionError: If `speed` is not within the range of 0.3 to 3.0.
        
        Example:
            >>> melo = Melo()
            >>> melo.load()  # Ensure model is loaded
            >>> melo.infer("Hello, world!", speaker_id=1, speed=1.2, audio_name="greeting")
        '''
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if self.model is None:
            raise UserWarning("Model not loaded. Run Melo.load() first.")
        
        if refine_prompt is not None:
            raise UserWarning("MeloTTS does not support refine_prompt.")
        
        if speaker_id is None:
            speaker = list(self.speaker_ids.keys())[0]
            speaker_id = list(self.speaker_ids.values())[0]
            print(f"Speaker ID not provided, using default speaker: {speaker}")
        assert 0.3 <= speed <= 3.0, "Speed should be between 0.3 and 3.0"
        if audio_name is None:
            output_path = None
        else:
            output_path = self.output_dir / f"{audio_name}.wav"
        return self.model.tts_to_file(text, speaker_id, speed=speed, output_path=output_path)
    
if __name__ == "__main__":
    model = Melo()
    # model.load()
    # for i in range(10):
    #     model.infer(f"Hello, world! {i}th sentence.", audio_name="hello_world")
    download_all_melo_model(model)
    # model.load('EN_V2')
    # model.infer("你好，我是MeloTTS生成的语音。", audio_name='hello_melo')