import os
import subprocess
from natsort import natsorted
from moviepy import VideoFileClip, CompositeVideoClip, vfx

def generate_video(input_dir, output_video="output.mp4"):
    images = natsorted([f for f in os.listdir(input_dir) if f.endswith(".png") and f.startswith("slide-")])
    audios = natsorted([f for f in os.listdir(input_dir) if f.endswith(".wav") and f.startswith("lecture-")])
    
    if len(images) != len(audios):
        print("Error: Number of images and audio files do not match!")
        return
    
    clips = []
    duration = .0
    
    for idx, (img, audio) in enumerate(zip(images, audios)):
        img_path = os.path.join(input_dir, img)
        audio_path = os.path.join(input_dir, audio)
        output_segment = os.path.join(input_dir, f"temp_{os.path.splitext(img)[0]}.mp4")
        
        # 创建单个图片+音频的视频片段, 末尾增加两秒静音
        # 获取音频时长(秒)
        audio_duration = float(subprocess.check_output([
            "ffprobe", "-i", audio_path, "-show_entries", "format=duration", 
            "-v", "quiet", "-of", "csv=%s" % ("p=0")
        ]).decode('utf-8').strip())

        # 视频总时长 = 音频时长 + 2秒静音
        video_duration = audio_duration + 2.0

        # 创建单个图片+音频的视频片段(末尾增加2秒静音)
        subprocess.run([
            "ffmpeg", "-y", 
            "-loop", "1", "-i", img_path, 
            "-i", audio_path,
            "-c:v", "libx264", "-tune", "stillimage", 
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", 
            "-t", str(video_duration),  # 设置总时长
            "-af", "apad=pad_dur=2",    # 在音频末尾填充2秒静音
            output_segment
        ])
        
        if idx == 0:
            clips.append(VideoFileClip(output_segment))
        else:
            clips.append(
                VideoFileClip(
                    output_segment
                ).with_start(
                    duration - idx
                ).with_effects(
                    [vfx.CrossFadeIn(1)]
                )
            )
        duration += clips[-1].duration
    
    # 合并所有片段，并添加过渡效果（交叉淡入淡出）
    output_path = os.path.join(input_dir, output_video)
    final_clips = CompositeVideoClip(clips)
    final_clips.write_videofile(output_path)
    final_clips.close()
    
    print(f"Video created: {output_path}")
    
    # 清理临时文件
    for img in images:
        temp_video = os.path.join(input_dir, f"temp_{os.path.splitext(img)[0]}.mp4")
        if os.path.exists(temp_video):
            os.remove(temp_video)

# 使用示例
generate_video("C:/Users/jerry/Documents/project/hduhelp-tts/assets/processed/ppt")
