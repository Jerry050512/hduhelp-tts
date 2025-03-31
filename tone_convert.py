import os
import torch
from pathlib import Path
from OpenVoice.openvoice import se_extractor
from OpenVoice.openvoice.api import ToneColorConverter

class ToneConvert:
    def __init__(self):
        self.ckpt_converter = Path('assets/checkpoints_v2/converter')
        self.base_speakers_ses = Path('assets/checkpoints_v2/base_speakers/ses')
        self.custom_speakers_ses = Path('assets/checkpoints_v2/custom_speakers/ses')
        self.output_dir = Path("assets/output/convert_audio")
        self.encode_message = "@HDU-Help"
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tone_color_converter = ToneColorConverter(
            self.ckpt_converter / 'config.json', 
            device=self.device
        )
        self.tone_color_converter.load_ckpt(self.ckpt_converter / 'checkpoint.pth')
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.custom_speakers_ses, exist_ok=True)
        self.target_se = None
        self.target_se_ckpt = None
        self.source_se = None

    def get_se(
            self, 
            ref_audio_file: str | None = None,
            ref_speaker_key: str | None = None, 
            src_audio_file: str | None = None, 
            speaker_key: str | None = None
        ):
        if ref_speaker_key:
            self.target_se = torch.load(
                self.custom_speakers_ses / f"{ref_speaker_key}.pth", 
                map_location=self.device
            )
        elif ref_audio_file:
            self.target_se, _ = se_extractor.get_se(
                ref_audio_file, 
                self.tone_color_converter, 
                "assets/processed",
                vad=True
            )
            self.target_se_ckpt = os.path.splitext(
                os.path.basename(ref_audio_file)
            )[0] + '.pth'
            
        
        if speaker_key:
            self.source_se = torch.load(
                self.base_speakers_ses / f"{speaker_key}.pth", 
                map_location=self.device
            )
        elif src_audio_file:
            self.source_se, _ = se_extractor.get_se(
                src_audio_file, 
                self.tone_color_converter, 
                "assets/processed",
                vad=True
            )
    
    def save_ref_se(self):
        if self.target_se is not None:
            torch.save(self.target_se, self.custom_speakers_ses / self.target_se_ckpt)
    
    def convert_tone_color(
            self, 
            src_audio_file: str, 
            output_path: str | None = None
        ):
        if self.source_se is None or self.target_se is None:
            raise ValueError("Please get source and target speaker embeddings first.")
        if output_path is None:
            output_path = os.path.join(
                self.output_dir, 
                os.path.basename(src_audio_file)
            )
        self.tone_color_converter.convert(
            src_audio_file, 
            self.source_se, 
            self.target_se, 
            output_path, 
            message=self.encode_message
        )
        return output_path
    
if __name__ == '__main__':
    print("Loading...")
    tc = ToneConvert()

    print("Getting speaker embeddings...")
    tc.get_se(
        ref_audio_file='assets/demo/ref-1.mp3', 
        # src_audio_file='assets/tts_audio/hello_world.wav', 
        speaker_key='zh'
    )
    # print("Saving speaker embeddings...")
    # tc.save_ref_se()
    print("Converting tone color...")
    tc.convert_tone_color('assets/processed/ppt/output.wav', output_path='assets/demo/converted.wav')