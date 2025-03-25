import os
import subprocess
from natsort import natsorted

def generate_video(input_dir, output_video="output.mp4"):
    images = natsorted([f for f in os.listdir(input_dir) if f.endswith(".png") and f.startswith("slide-")])
    audios = natsorted([f for f in os.listdir(input_dir) if f.endswith(".wav") and f.startswith("lecture-")])
    
    if len(images) != len(audios):
        print("Error: Number of images and audio files do not match!")
        return
    
    temp_list_file = os.path.join(input_dir, "input_list.txt")
    
    with open(temp_list_file, "w", encoding="utf-8") as f:
        for img, audio in zip(images, audios):
            img_path = os.path.join(input_dir, img)
            audio_path = os.path.join(input_dir, audio)
            output_segment = os.path.join(input_dir, f"temp_{os.path.splitext(img)[0]}.mp4")
            
            # 创建单个图片+音频的视频片段
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", audio_path,
                "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p", "-shortest", output_segment
            ])
            f.write(f"file '{output_segment}'\n")
    
    # 合并所有片段，
    # TODO: 并添加过渡效果（交叉淡入淡出）
    output_path = os.path.join(input_dir, output_video)
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", temp_list_file,
        "-c", "copy", output_path
    ])
    
    print(f"Video created: {output_path}")
    
    # 清理临时文件
    os.remove(temp_list_file)
    for img in images:
        temp_video = os.path.join(input_dir, f"temp_{os.path.splitext(img)[0]}.mp4")
        if os.path.exists(temp_video):
            os.remove(temp_video)

# 使用示例
generate_video("C:/Users/jerry/Documents/project/hduhelp-tts/assets/processed/ppt")
