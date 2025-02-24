import os
from pydub import AudioSegment

def concatenate_audio_files(input_files, output_file, remove_inputs=False):
    """
    Concatenates multiple audio files into a single output file.

    Args:
        input_files: A list of file paths to the audio files to concatenate.
        output_file: The file path for the output concatenated audio file.
        remove_inputs: If True, delete the input files after successful concatenation.

    Returns:
        True if the concatenation was successful, False otherwise.
    """
    if not input_files:
        print("Error: No input files provided.")
        return False

    try:
        combined_audio = AudioSegment.from_file(input_files[0])

        for file_path in input_files[1:]:
            audio_segment = AudioSegment.from_file(file_path)
            combined_audio += audio_segment

        combined_audio.export(output_file, format=os.path.splitext(output_file)[1][1:])

        if remove_inputs:
            for file_path in input_files:
                os.remove(file_path)
                print(f"Removed input file: {file_path}")

        return True

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Example Usage:

def example():
    input_audio_files = ["audio1.wav", "audio2.mp3", "audio3.ogg"]
    output_audio_file = "assets/demo/combined_audio.mp3"

    # Create dummy audio files for demonstration if they don't exist
    if not os.path.exists("audio1.wav"):
        silent_wav = AudioSegment.silent(duration=2000)
        silent_wav.export("audio1.wav", format="wav")
    if not os.path.exists("audio2.mp3"):
        silent_mp3 = AudioSegment.silent(duration=3000)
        silent_mp3.export("audio2.mp3", format="mp3")
    if not os.path.exists("audio3.ogg"):
        silent_ogg = AudioSegment.silent(duration=1000)
        silent_ogg.export("audio3.ogg", format="ogg")

    if concatenate_audio_files(input_audio_files, output_audio_file, remove_inputs=True): #removed inputs set to true here.
        print(f"Audio files concatenated successfully to {output_audio_file}")
    else:
        print("Audio file concatenation failed.")

if __name__ == "__main__":
    example()