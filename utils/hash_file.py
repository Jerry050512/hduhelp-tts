import os
import hashlib
import time
import datetime

def generate_unique_filename_hash(input_files, output_extension, timestamp=True, hash_length=16):
    """
    Generates a unique, fixed-length filename using a hash of the input files.

    Args:
        input_files: A list of input file paths.
        output_extension: The desired output file extension (e.g., ".mp3", ".wav").
        timestamp: If True, adds a timestamp to the filename.
        hash_length: The desired length of the hash portion of the filename.

    Returns:
        A unique, fixed-length filename.
    """
    if not input_files:
        raise ValueError("Input file list cannot be empty.")

    combined_data = b""  # Initialize an empty byte string
    for file_path in input_files:
        try:
            with open(file_path, "rb") as f:
                combined_data += f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

    # Generate a hash of the combined file data
    hash_object = hashlib.sha256(combined_data)
    hex_digest = hash_object.hexdigest()
    truncated_hash = hex_digest[:hash_length]

    filename = truncated_hash

    if timestamp:
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")[2:]
        filename = f"{timestamp_str}_{truncated_hash}"

    return f"{filename}{output_extension}"

def generate_text_hash_filename(text, file_ext, hash_algorithm="sha256", hash_length=16, timestamp=True):
    """
    Generates a hash-based filename for a given text, with optional timestamp and file extension.

    Args:
        text (str): The input text.
        file_ext (str): The file extension (e.g., ".txt", ".mp3").
        hash_algorithm (str): The hash algorithm to use (e.g., "sha256", "md5").
        hash_length (int): The desired length of the truncated hash.
        timestamp (bool): If True, adds a timestamp to the filename.

    Returns:
        str: The generated filename.
    """
    try:
        hash_object = hashlib.new(hash_algorithm)
        hash_object.update(text.encode("utf-8"))
        hex_digest = hash_object.hexdigest()
        truncated_hash = hex_digest[:hash_length]

        filename = truncated_hash

        if timestamp:
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp_str}_{truncated_hash}"

        return f"{filename}{file_ext}"

    except ValueError:
        return "Invalid hash algorithm."

# Example Usage:
def example():
    input_files = ["audio1.wav", "audio2.mp3", "audio3.ogg"]
    output_extension = ".mp3"

    # Create dummy audio files for demonstration
    if not os.path.exists("audio1.wav"):
        silent_wav = AudioSegment.silent(duration=2000)
        silent_wav.export("audio1.wav", format="wav")
    if not os.path.exists("audio2.mp3"):
        silent_mp3 = AudioSegment.silent(duration=3000)
        silent_mp3.export("audio2.mp3", format="mp3")
    if not os.path.exists("audio3.ogg"):
        silent_ogg = AudioSegment.silent(duration=1000)
        silent_ogg.export("audio3.ogg", format="ogg")

    try:
        unique_filename = generate_unique_filename_hash(input_files, output_extension)
        print(f"Unique filename: {unique_filename}")

        unique_filename_no_timestamp = generate_unique_filename_hash(input_files, output_extension, timestamp=False, hash_length=8)
        print(f"Unique filename without timestamp: {unique_filename_no_timestamp}")

        for file in input_files:
            os.remove(file)

    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    from pydub import AudioSegment #moved import here so it only runs if example is called.
    example()
    print(generate_text_hash_filename("Hello, world!", ".txt"))