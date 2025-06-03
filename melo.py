from MeloTTS.melo.api import TTS
from pathlib import Path
import os
import torch
from utils.download_all_tts_model import download_all_melo_model
import glob
from os.path import join, basename, splitext

class Melo:
    def __init__(self, output_dir, sample_rate=44100, language=None): # output_dir is now a required positional argument
        self.model: TTS | None = None
        self.speaker_ids: dict | None = None
        self.sample_rate = sample_rate
        self.output_dir = output_dir if isinstance(output_dir, Path) else Path(output_dir) # Uses the provided output_dir
        self.language: str | None = language

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
            output_path: str | Path | None, # Changed from audio_name to output_path
            speaker_id: int | None = None,
            speed=1.0,
            refine_prompt: str | None = None
        ):
        '''
        Generate audio from text using MeloTTS.
                
        Args:
            text (str): The input text to be converted into speech.
            output_path (str | Path | None): The full path (including filename and extension) to save the audio.
                                             If None, audio is not saved to file (behavior of tts_to_file).
            speaker_id (int | None, optional): The ID of the speaker to use. If None, the default speaker will be selected.
            speed (float, optional): The speed of speech synthesis. Should be between 0.3 and 3.0. Defaults to 1.0.
            refine_prompt (str | None, optional): Not supported in MeloTTS. If provided, a UserWarning will be raised.
        
        Returns:
            None: The synthesized speech is directly processed by the model. (Note: tts_to_file might return the path or audio data)
        
        Raises:
            UserWarning: If the model is not loaded before inference.
            UserWarning: If `refine_prompt` is provided, as it is not supported.
            AssertionError: If `speed` is not within the range of 0.3 to 3.0.
        
        Example:
            >>> melo = Melo(output_dir="/some/default/output") # output_dir is now required
            >>> melo.load()  # Ensure model is loaded
            >>> melo.infer("Hello, world!", output_path="/tmp/greeting.wav", speaker_id=1, speed=1.2)
        '''
        # Directory creation for self.output_dir is removed.
        # The server/caller is responsible for managing directories for output_path.
        if self.model is None:
            raise UserWarning("Model not loaded. Run Melo.load() first.")
        
        if refine_prompt is not None:
            raise UserWarning("MeloTTS does not support refine_prompt.")
        
        if speaker_id is None:
            speaker = list(self.speaker_ids.keys())[0]
            speaker_id = list(self.speaker_ids.values())[0]
            print(f"Speaker ID not provided, using default speaker: {speaker}")
        assert 0.3 <= speed <= 3.0, "Speed should be between 0.3 and 3.0"

        # output_path is now passed directly to tts_to_file.
        # If output_path is None, tts_to_file handles it (doesn't save, might return audio data).
        # If output_path is a string or Path, tts_to_file attempts to save there.
        return self.model.tts_to_file(text, speaker_id, speed=speed, output_path=output_path)
    
if __name__ == "__main__":
    # Example usage reflecting changes: output_dir is now mandatory.
    model = Melo(output_dir=Path("assets/processed/ppt"))
    # model.load()
    # for i in range(10):
    #     # audio_name changed to output_path, requires full path if saving
    #     model.infer(f"Hello, world! {i}th sentence.", output_path=Path("assets/processed/ppt") / f"hello_world_{i}.wav")
    # download_all_melo_model(model)
    # model.load('EN_V2')
    # model.infer("你好，我是MeloTTS生成的语音。", output_path=Path("assets/processed/ppt") / 'hello_melo.wav')

    model.load('ZH')
    for text_file in glob.glob("assets/processed/ppt/lecture-*.txt"):
        with open(text_file, 'r', encoding='utf-8') as f:
            text = f.read()
        print(f"Infering: \n{text}\n")
        # audio_name changed to output_path, construct full path
        output_filename = Path("assets/processed/ppt") / f"{splitext(basename(text_file))[0]}.wav"
        model.infer(text, output_path=output_filename)