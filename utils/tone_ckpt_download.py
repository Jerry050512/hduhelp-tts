import requests
import zipfile
import os

url = "https://myshell-public-repo-host.s3.amazonaws.com/openvoice/checkpoints_v2_0417.zip"
download_path = "checkpoints_v2_0417.zip"
extract_path = "./assets/"

try:
    print(f"Downloading from {url} to {download_path}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    with open(download_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"Downloaded successfully to {download_path}")

    print(f"Creating directory {extract_path} if it doesn't exist...")
    os.makedirs(extract_path, exist_ok=True)
    print(f"Directory {extract_path} is ready.")

    print(f"Extracting {download_path} to {extract_path}...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    print(f"Extracted successfully to {extract_path}")

    print("Cleanup: Removing downloaded zip file...")
    os.remove(download_path)
    print(f"Removed {download_path}")

    print("Download and extraction complete!")

except requests.exceptions.RequestException as e:
    print(f"Download failed: {e}")
except zipfile.BadZipFile as e:
    print(f"Extraction failed: Bad zip file - {e}")
except Exception as e:
    print(f"An error occurred: {e}")