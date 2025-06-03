import os
import torch
from pathlib import Path
from OpenVoice.openvoice import se_extractor
from OpenVoice.openvoice.api import ToneColorConverter

class ToneConvert:
    def __init__(self, custom_speakers_ses_dir, output_dir): # Parameters added
        self.ckpt_converter = Path('assets/checkpoints_v2/converter') # Remains hardcoded
        self.base_speakers_ses = Path('assets/checkpoints_v2/base_speakers/ses') # Remains hardcoded
        self.custom_speakers_ses = Path(custom_speakers_ses_dir) # Use parameter
        self.output_dir = Path(output_dir) # Use parameter
        self.encode_message = "@HDU-Help"
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tone_color_converter = ToneColorConverter(
            self.ckpt_converter / 'config.json', 
            device=self.device
        )
        self.tone_color_converter.load_ckpt(self.ckpt_converter / 'checkpoint.pth')
        
        # Using new parameter-based paths for directory creation
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.custom_speakers_ses, exist_ok=True)
        self.target_se = None
        self.target_se_ckpt = None # This will be a filename, e.g., "ref_speaker.pth"
        self.source_se = None

    def get_se(
            self,
            intermediate_dir, # Parameter added
            ref_audio_file: str | None = None,
            ref_speaker_key: str | None = None, 
            src_audio_file: str | None = None, 
            speaker_key: str | None = None
        ):
        if ref_speaker_key:
            # self.custom_speakers_ses is now from constructor
            self.target_se = torch.load(
                self.custom_speakers_ses / f"{ref_speaker_key}.pth", 
                map_location=self.device
            )
        elif ref_audio_file:
            self.target_se, _ = se_extractor.get_se(
                ref_audio_file, 
                self.tone_color_converter, 
                intermediate_dir, # Use intermediate_dir parameter
                vad=True
            )
            # self.target_se_ckpt is just the filename
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
                intermediate_dir, # Use intermediate_dir parameter
                vad=True
            )
    
    def save_ref_se(self):
        if self.target_se is not None and self.target_se_ckpt is not None:
            # self.custom_speakers_ses from constructor, self.target_se_ckpt is filename
            torch.save(self.target_se, self.custom_speakers_ses / self.target_se_ckpt)
    
    def convert_tone_color(
            self, 
            src_audio_file: str, 
            output_filepath: str | Path # Changed from output_path to output_filepath (full path)
        ):
        if self.source_se is None or self.target_se is None:
            raise ValueError("Please get source and target speaker embeddings first.")

        # Removed old logic for constructing output_path using self.output_dir
        # output_filepath is now a full path provided by the caller.

        self.tone_color_converter.convert(
            src_audio_file, 
            self.source_se, 
            self.target_se, 
            str(output_filepath), # Use output_filepath directly, ensure it's string for the API
            message=self.encode_message
        )
        return str(output_filepath) # Return the provided output_filepath
    
if __name__ == '__main__':
    print("Loading...")
    # Example usage reflecting changes: custom_speakers_ses_dir and output_dir are now mandatory.
    temp_custom_ses_dir = Path("./temp_custom_ses")
    temp_output_conversion_dir = Path("./temp_converted_audio")

    tc = ToneConvert(
        custom_speakers_ses_dir=temp_custom_ses_dir,
        output_dir=temp_output_conversion_dir
    )

    print("Getting speaker embeddings...")
    # intermediate_dir is now required for get_se
    temp_intermediate_processing_dir = Path("./temp_intermediate_se")
    os.makedirs(temp_intermediate_processing_dir, exist_ok=True)

    tc.get_se(
        intermediate_dir=temp_intermediate_processing_dir,
        ref_audio_file='assets/demo/ref-1.mp3', 
        speaker_key='zh'
    )

    print("Saving reference speaker embedding (if extracted)...")
    tc.save_ref_se() # Will save to temp_custom_ses_dir / "ref-1.pth"

    print("Converting tone color...")
    # output_path changed to output_filepath, requires full path.
    converted_audio_output_filepath = temp_output_conversion_dir / "converted_demo.wav"
    # Ensure the source file exists for the test to run
    os.makedirs("assets/processed/ppt", exist_ok=True)
    with open("assets/processed/ppt/output.wav", "w") as f: f.write("dummy audio data") # Create dummy file

    tc.convert_tone_color(
        'assets/processed/ppt/output.wav',
        output_filepath=converted_audio_output_filepath
    )
    print(f"Converted audio saved to: {converted_audio_output_filepath}")